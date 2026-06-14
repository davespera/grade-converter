from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

# Prevent import-time failures in backend.database when running tests outside Docker.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./_placeholder_test.db")
os.environ.setdefault("FASTAPI_ACTIVEPIECES_API_KEY", "test-activepieces-key")

AUTH_HEADERS = {"x-api-key": os.environ["FASTAPI_ACTIVEPIECES_API_KEY"]}

from backend import database, models
from backend.database import Base
from backend.routers import scales, transfer


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


def _eq(origin_grade: str) -> dict:
    """A minimal equivalence row; only origin_grade matters for matching."""
    return {
        "origin_grade": origin_grade,
        "spanish_5_10": Decimal("5.00"),
        "spanish_1_4": 1,
        "spanish_literal": models.SpanishLiteralEnum.APROBADO,
    }


# Two scales for the same country with different grade sets, plus a third scale
# under a different country, so matching/ranking can be exercised end-to-end.
_SCALES = [
    ("ALEMANIA", "letters", ["A", "B", "C", "D"]),
    ("ALEMANIA", "numbers", ["1,0", "2,0", "3,0"]),
    ("FRANCIA", "french", ["AB", "B", "TB"]),
    # Two same-size scales that both fully cover {"18", "30"} -> ambiguous tie.
    ("ITALIA", "scale-a", ["18", "30"]),
    ("ITALIA", "scale-b", ["18", "30"]),
]


async def _setup_schema_and_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        for country_name, scale_description, grades in _SCALES:
            scale = models.AcademicScale(
                country_name=country_name,
                scale_description=scale_description,
            )
            session.add(scale)
            await session.flush()
            for grade in grades:
                session.add(models.GradeEquivalence(scale_id=scale.id, **_eq(grade)))
        await session.commit()


async def _teardown_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def _make_client() -> TestClient:
    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session
    return TestClient(app)


def test_match_ranks_fully_covering_scale_first() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.post(
            "/scales/match",
            json={"country": "alemania", "grades": ["1,0", "2,0", "3,0"]},
        )
        payload = response.json()

        assert response.status_code == 200
        # Both ALEMANIA scales are returned; the numeric one fully covers the query.
        assert len(payload) == 2
        top = payload[0]
        assert top["scale_description"] == "numbers"
        assert top["coverage"] == 1.0
        assert top["matched_count"] == 3
        assert top["total_query_grades"] == 3
        assert top["unmatched_grades"] == []
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_match_reports_unmatched_grades_for_partial_scale() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.post(
            "/scales/match",
            json={"country": "alemania", "grades": ["A", "B", "Z"]},
        )
        payload = response.json()

        assert response.status_code == 200
        top = payload[0]
        assert top["scale_description"] == "letters"
        assert top["matched_count"] == 2
        assert top["coverage"] == 2 / 3
        assert top["unmatched_grades"] == ["Z"]
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_match_dedupes_query_grades() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.post(
            "/scales/match",
            json={"country": "francia", "grades": ["B", "B", "TB"]},
        )
        payload = response.json()

        assert response.status_code == 200
        top = payload[0]
        # Duplicate "B" collapses to a 2-grade query set, both covered.
        assert top["total_query_grades"] == 2
        assert top["matched_count"] == 2
        assert top["coverage"] == 1.0
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_match_unknown_country_returns_empty_list() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.post(
            "/scales/match",
            json={"country": "nowhere", "grades": ["A"]},
        )

        assert response.status_code == 200
        assert response.json() == []
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_match_keeps_tied_candidates_so_workflow_can_detect_ambiguity() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.post(
            "/scales/match",
            json={"country": "italia", "grades": ["18", "30"]},
        )
        payload = response.json()

        assert response.status_code == 200
        assert len(payload) == 2
        # Both scales fully cover the query with the same total size: a tie that the
        # workflow's confidence rule must treat as ambiguous (not a confident pick).
        first, second = payload[0], payload[1]
        assert first["coverage"] == second["coverage"] == 1.0
        assert first["scale_total_grades"] == second["scale_total_grades"]
        assert {first["scale_description"], second["scale_description"]} == {"scale-a", "scale-b"}
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_match_then_transfer_covered_grades_end_to_end() -> None:
    """Mirror the workflow's backend contract: /scales/match resolves the scale,
    then /transfer converts only the grades that scale covers."""
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)

        # "Z" is not in any ALEMANIA scale; the letters scale covers A, B, C.
        extracted = [
            {"subject": "Maths", "origin_grade": "A"},
            {"subject": "Physics", "origin_grade": "B"},
            {"subject": "History", "origin_grade": "C"},
            {"subject": "Latin", "origin_grade": "Z"},
        ]
        distinct = sorted({g["origin_grade"] for g in extracted})

        match = client.post(
            "/scales/match", json={"country": "ALEMANIA", "grades": distinct}
        )
        candidates = match.json()
        top = candidates[0]
        assert top["scale_description"] == "letters"
        assert top["unmatched_grades"] == ["Z"]

        # Filter to the covered grades, exactly as the workflow does.
        unmatched = set(top["unmatched_grades"])
        covered = [g for g in extracted if g["origin_grade"] not in unmatched]

        transfer_res = client.post(
            "/transfer",
            json={"scale_id": top["scale_id"], "grades": covered},
            headers=AUTH_HEADERS,
        )
        payload = transfer_res.json()

        assert transfer_res.status_code == 200
        assert [c["origin_grade"] for c in payload["conversion"]] == ["A", "B", "C"]
        assert payload["conversion"][0]["subject"] == "Maths"
        # Seeded equivalences all map to APROBADO / 5.00 (see _eq).
        assert {c["converted_literal"] for c in payload["conversion"]} == {"APROBADO"}
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())
