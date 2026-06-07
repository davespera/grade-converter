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
from backend.routers import transfer


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
            scale_description="A-F",
        )
        session.add(scale)
        await session.flush()

        session.add(
            models.GradeEquivalence(
                scale_id=scale.id,
                origin_grade="A",
                spanish_5_10=Decimal("9.00"),
                spanish_1_4=3,
                spanish_literal=models.SpanishLiteralEnum.SOBRESALIENTE,
            )
        )

        await session.commit()


async def _teardown_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def test_convert_grade_requires_api_key_header() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session
    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/transfer",
            json={"scale_id": 1, "grades": [{"origin_grade": "A"}]},
        )

        assert response.status_code == 401
        assert response.json()["detail"] in {
            "Not authenticated",
            "Missing or invalid API key",
        }
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_convert_grade_rejects_invalid_api_key() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session
    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/transfer",
            json={"scale_id": 1, "grades": [{"origin_grade": "A"}]},
            headers={"x-api-key": "invalid-key"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Missing or invalid API key"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_convert_grade_allows_valid_api_key() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(transfer.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session
    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/transfer",
            json={"scale_id": 1, "grades": [{"origin_grade": "A"}]},
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["conversion"][0]["origin_grade"] == "A"
        assert payload["conversion"][0]["converted_literal"] == "SOBRESALIENTE"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())
