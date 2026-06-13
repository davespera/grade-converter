from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

# Prevent import-time failures in backend.database when running tests outside Docker.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./_placeholder_test.db")

from backend import database, models
from backend.database import Base
from backend.routers import scales


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


# (country_name, scale_description) rows covering two countries and multiple
# scales per country, so search filtering can be exercised end-to-end.
_SCALE_ROWS = [
    ("ALEMANIA", "1-6"),
    ("ALEMANIA", "1-5"),
    ("AFGANISTAN", "50(1ª)-100(51ª)"),
]


async def _setup_schema_and_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        for country_name, scale_description in _SCALE_ROWS:
            session.add(
                models.AcademicScale(
                    country_name=country_name,
                    scale_description=scale_description,
                )
            )
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


def test_search_by_country_is_case_insensitive_and_contains_matched() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        # Lowercase, partial term still matches the uppercase "ALEMANIA" key.
        response = client.get("/scales/search", params={"country": "alem"})
        payload = response.json()

        assert response.status_code == 200
        assert isinstance(payload, list)
        assert len(payload) == 2
        assert {item["country_name"] for item in payload} == {"ALEMANIA"}
        assert {item["scale_description"] for item in payload} == {"1-6", "1-5"}
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_search_results_are_lightweight_without_equivalences() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.get("/scales/search", params={"country": "alemania"})
        payload = response.json()

        assert response.status_code == 200
        assert len(payload) >= 1
        for item in payload:
            assert "id" in item
            assert "country_name" in item
            assert "scale_description" in item
            # AcademicScaleList must not carry the nested equivalences.
            assert "equivalences" not in item
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_search_with_scale_description_narrows_to_specific_scale() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.get(
            "/scales/search",
            params={"country": "alemania", "scale_description": "1-6"},
        )
        payload = response.json()

        assert response.status_code == 200
        assert len(payload) == 1
        assert payload[0]["country_name"] == "ALEMANIA"
        assert payload[0]["scale_description"] == "1-6"
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_search_without_filters_returns_all_scales() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.get("/scales/search")
        payload = response.json()

        assert response.status_code == 200
        assert len(payload) == len(_SCALE_ROWS)
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_search_with_no_match_returns_empty_list() -> None:
    asyncio.run(_setup_schema_and_seed())

    client = None
    try:
        client = _make_client()
        response = client.get("/scales/search", params={"country": "nowhere"})
        payload = response.json()

        assert response.status_code == 200
        assert payload == []
    finally:
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())
