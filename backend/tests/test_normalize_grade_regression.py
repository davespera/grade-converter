from __future__ import annotations

import asyncio
import os
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

# Prevent import-time failures in backend.database when running tests outside Docker.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./_placeholder_test.db")
os.environ.setdefault("FASTAPI_ACTIVEPIECES_API_KEY", "test-activepieces-key")

AUTH_HEADERS = {"x-api-key": os.environ["FASTAPI_ACTIVEPIECES_API_KEY"]}

from backend import crud, database, models
from backend.database import Base
from backend.routers import transfer


# --- Pure-function tests for crud.normalize_grade -------------------------------
# normalize_grade underpins both /transfer lookups and /scales/match coverage, so
# its contract is pinned here independently of any DB or endpoint.

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Integer-looking grades gain two decimals and a comma separator.
        ("9", "9,00"),
        ("18", "18,00"),
        # Dot decimal separator is accepted and rewritten as a comma.
        ("9.0", "9,00"),
        ("8.5", "8,50"),
        # Comma decimal separator is preserved (just zero-padded).
        ("9,5", "9,50"),
        ("10,00", "10,00"),
        # Rounding to two decimal places (non-midpoint values to avoid float ties).
        ("7.124", "7,12"),
        ("7.126", "7,13"),
        ("8.999", "9,00"),
    ],
)
def test_normalize_grade_numeric_values(raw: str, expected: str) -> None:
    assert crud.normalize_grade(raw) == expected


@pytest.mark.parametrize("raw", ["A", "AB", "TB", "Notable", "50(1ª)"])
def test_normalize_grade_leaves_non_numeric_grades_unchanged(raw: str) -> None:
    # Letter grades / codes must pass through untouched so exact matching still works.
    assert crud.normalize_grade(raw) == raw


def test_normalize_grade_is_idempotent_for_numeric_values() -> None:
    once = crud.normalize_grade("9")
    assert crud.normalize_grade(once) == once == "9,00"


# --- Integration: /transfer round-trips numeric grades through normalize_grade --
# Existing transfer tests only use letter grades; this pins the promise that a
# numeric grade stored in its normalized "9,00" form is found regardless of how
# the caller spells the same value ("9", "9.0", "9,00").

engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def _override_db_session():
    async with TestSessionLocal() as session:
        yield session


async def _setup_schema_and_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        scale = models.AcademicScale(
            country_name="TESTLAND",
            scale_description="0-10",
        )
        session.add(scale)
        await session.flush()

        # Grades are stored in their normalized form, exactly as seed.py would.
        session.add(
            models.GradeEquivalence(
                scale_id=scale.id,
                origin_grade="9,00",
                spanish_5_10=Decimal("9.00"),
                spanish_1_4=3,
                spanish_literal=models.SpanishLiteralEnum.SOBRESALIENTE,
            )
        )
        session.add(
            models.GradeEquivalence(
                scale_id=scale.id,
                origin_grade="8,50",
                spanish_5_10=Decimal("8.50"),
                spanish_1_4=3,
                spanish_literal=models.SpanishLiteralEnum.NOTABLE,
            )
        )
        await session.commit()


async def _teardown_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.parametrize("spelling", ["9", "9.0", "9,00", "9.00"])
def test_convert_grade_matches_numeric_grade_regardless_of_spelling(spelling: str) -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/transfer",
            json={"scale_id": 1, "grades": [{"origin_grade": spelling}]},
            headers=AUTH_HEADERS,
        )
        payload = response.json()

        assert response.status_code == 200
        assert len(payload["conversion"]) == 1
        # The stored (normalized) origin_grade is echoed back, not the raw input.
        assert payload["conversion"][0]["origin_grade"] == "9,00"
        assert payload["conversion"][0]["converted_5_10"] == "9.00"
        assert payload["conversion"][0]["converted_literal"] == "SOBRESALIENTE"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_convert_grade_rounds_caller_value_before_lookup() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        # "8.504" rounds to "8,50", which matches the stored equivalence.
        response = client.post(
            "/transfer",
            json={"scale_id": 1, "grades": [{"origin_grade": "8.504"}]},
            headers=AUTH_HEADERS,
        )
        payload = response.json()

        assert response.status_code == 200
        assert payload["conversion"][0]["origin_grade"] == "8,50"
        assert payload["conversion"][0]["converted_literal"] == "NOTABLE"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())
