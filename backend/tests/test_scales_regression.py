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


async def _setup_schema_and_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        scale = models.AcademicScale(
            country_name="TESTLAND",
            scale_description="A-F",
            total_grades=6,
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


def test_get_scales_includes_equivalences_regression() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.get("/scales/")
        payload = response.json()

        assert response.status_code == 200
        assert isinstance(payload, list)
        assert len(payload) == 1
        assert "equivalences" in payload[0]
        assert isinstance(payload[0]["equivalences"], list)
        assert len(payload[0]["equivalences"]) == 1
        assert payload[0]["equivalences"][0]["origin_grade"] == "A"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_get_scales_handles_mixed_equivalence_collections_regression() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        async def _insert_second_scale_without_equivalences() -> None:
            async with TestSessionLocal() as session:
                session.add(
                    models.AcademicScale(
                        country_name="EMPTYLAND",
                        scale_description="0-100",
                        total_grades=101,
                    )
                )
                await session.commit()

        asyncio.run(_insert_second_scale_without_equivalences())

        client = TestClient(app)
        response = client.get("/scales/")
        payload = response.json()

        assert response.status_code == 200
        assert isinstance(payload, list)
        assert len(payload) == 2

        by_country = {item["country_name"]: item for item in payload}
        assert "TESTLAND" in by_country
        assert "EMPTYLAND" in by_country

        assert isinstance(by_country["TESTLAND"]["equivalences"], list)
        assert len(by_country["TESTLAND"]["equivalences"]) == 1
        assert by_country["TESTLAND"]["equivalences"][0]["origin_grade"] == "A"

        assert isinstance(by_country["EMPTYLAND"]["equivalences"], list)
        assert by_country["EMPTYLAND"]["equivalences"] == []
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_get_scale_by_id_includes_equivalences_regression() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.get("/scales/1")
        payload = response.json()

        assert response.status_code == 200
        assert payload["id"] == 1
        assert payload["country_name"] == "TESTLAND"
        assert isinstance(payload["equivalences"], list)
        assert len(payload["equivalences"]) == 1
        assert payload["equivalences"][0]["origin_grade"] == "A"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_get_scale_by_id_returns_404_for_missing_scale() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.get("/scales/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Scale not found"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_create_scale_returns_new_scale_with_empty_equivalences() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/scales/",
            json={
                "country_name": "SPAIN",
                "scale_description": "0-10",
                "total_grades": 11,
            },
        )
        payload = response.json()

        assert response.status_code == 200
        assert payload["country_name"] == "SPAIN"
        assert payload["scale_description"] == "0-10"
        assert payload["total_grades"] == 11
        assert "id" in payload
        assert payload["equivalences"] == []
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_create_equivalence_for_scale_returns_created_equivalence() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)
        response = client.post(
            "/scales/1/equivalences/",
            json={
                "origin_grade": "B",
                "spanish_5_10": 8.5,
                "spanish_1_4": 3,
                "spanish_literal": "SOBRESALIENTE",
            },
        )
        payload = response.json()

        assert response.status_code == 200
        assert payload["scale_id"] == 1
        assert payload["origin_grade"] == "B"
        assert payload["spanish_5_10"] == "8.50"
        assert payload["spanish_1_4"] == 3
        assert payload["spanish_literal"] == "SOBRESALIENTE"
        assert "id" in payload
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_delete_equivalence_for_scale_removes_equivalence() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)

        # Delete the existing equivalence (seed creates equivalence with id 1)
        response = client.delete("/scales/1/equivalences/1")
        assert response.status_code == 200

        # Verify equivalence is no longer present on the scale
        response = client.get("/scales/1")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload["equivalences"], list)
        assert payload["equivalences"] == []
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_delete_scale_removes_scale_and_equivalences() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)

        # Delete the scale
        response = client.delete("/scales/1")
        assert response.status_code == 200

        # The scale should no longer be retrievable
        response = client.get("/scales/1")
        assert response.status_code == 404
        assert response.json()["detail"] == "Scale not found"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_update_scale_patches_fields_and_keeps_equivalences_regression() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)

        response = client.patch(
            "/scales/1",
            json={"scale_description": "Updated A-F", "total_grades": 7},
        )
        payload = response.json()

        assert response.status_code == 200
        assert payload["id"] == 1
        assert payload["scale_description"] == "Updated A-F"
        assert payload["total_grades"] == 7
        assert isinstance(payload["equivalences"], list)
        assert len(payload["equivalences"]) == 1
        assert payload["equivalences"][0]["origin_grade"] == "A"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())


def test_update_equivalence_changes_values_regression() -> None:
    asyncio.run(_setup_schema_and_seed())

    app = FastAPI()
    app.include_router(scales.router)
    app.dependency_overrides[database.get_database_session] = _override_db_session

    client = None
    try:
        client = TestClient(app)

        # Update the existing equivalence created by the seed (id 1)
        response = client.patch(
            "/scales/1/equivalences/1",
            json={"spanish_5_10": 9.50, "spanish_literal": "APROBADO"},
        )
        payload = response.json()

        assert response.status_code == 200
        assert payload["id"] == 1
        assert payload["scale_id"] == 1
        assert payload["spanish_5_10"] == "9.50"
        assert payload["spanish_literal"] == "APROBADO"
    finally:
        app.dependency_overrides.clear()
        if client is not None:
            client.close()
        asyncio.run(_teardown_schema())