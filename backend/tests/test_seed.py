from __future__ import annotations

import asyncio
import json
import os
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

# Prevent import-time failures in backend.database when running tests outside Docker.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./_placeholder_test.db")

from backend import models
from backend.database import Base
from backend.seed import load_scales, seed


SAMPLE_DATA = {
    "paises": {
        "TESTLAND": {
            "nombre": "TESTLAND",
            "escalas": [
                {
                    "id_escala": "0-100",
                    "calificaciones": {
                        "50,00": {
                            "equivalente_5_10": 5.0,
                            "equivalente_1_4": 1,
                            "equivalente_literal": "APROBADO",
                        },
                        "100,00": {
                            "equivalente_5_10": 10.0,
                            "equivalente_1_4": 4,
                            "equivalente_literal": "MATRICULA DE HONOR",
                        },
                    },
                },
                {
                    "id_escala": "A-F",
                    "calificaciones": {
                        "A": {
                            "equivalente_5_10": 9.13,
                            "equivalente_1_4": 3,
                            "equivalente_literal": "SOBRESALIENTE",
                        },
                    },
                },
            ],
        },
        "OTHERLAND": {
            "nombre": "OTHERLAND",
            "escalas": [
                {
                    "id_escala": "1-5",
                    "calificaciones": {
                        "4,00": {
                            "equivalente_5_10": 7.5,
                            "equivalente_1_4": 2,
                            "equivalente_literal": "NOTABLE",
                        },
                    },
                },
            ],
        },
    },
}


def _write_sample_json(tmp_path: Path) -> Path:
    json_path = tmp_path / "equivalences.json"
    json_path.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")
    return json_path


def _make_engine_and_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return engine, factory


def test_load_scales_maps_json_to_model_rows(tmp_path: Path) -> None:
    json_path = _write_sample_json(tmp_path)

    scales = load_scales(json_path)

    assert len(scales) == 3
    scale_row, equivalence_rows = scales[0]
    assert scale_row == {"country_name": "TESTLAND", "scale_description": "0-100"}
    assert len(equivalence_rows) == 2
    assert equivalence_rows[1] == {
        "origin_grade": "100,00",
        "spanish_5_10": Decimal("10.0"),
        "spanish_1_4": 4,
        "spanish_literal": models.SpanishLiteralEnum.MATRICULA_DE_HONOR,
    }


def test_seed_populates_empty_database(tmp_path: Path) -> None:
    json_path = _write_sample_json(tmp_path)
    engine, factory = _make_engine_and_factory()

    async def _run() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        n_scales, n_equivalences = await seed(json_path=json_path, session_factory=factory)
        assert (n_scales, n_equivalences) == (3, 4)

        async with factory() as session:
            scale_count = await session.scalar(select(func.count()).select_from(models.AcademicScale))
            assert scale_count == 3

            honor = (
                await session.exec(
                    select(models.GradeEquivalence).where(
                        models.GradeEquivalence.origin_grade == "100,00"
                    )
                )
            ).scalar_one()
            assert honor.spanish_literal == models.SpanishLiteralEnum.MATRICULA_DE_HONOR
            assert honor.spanish_literal.value == "MATRICULA DE HONOR"
            assert honor.spanish_5_10 == Decimal("10.00")
            assert honor.scale is not None
            assert honor.scale.country_name == "TESTLAND"

        await engine.dispose()

    asyncio.run(_run())


def test_seed_skips_populated_database_unless_forced(tmp_path: Path) -> None:
    json_path = _write_sample_json(tmp_path)
    engine, factory = _make_engine_and_factory()

    async def _run() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await seed(json_path=json_path, session_factory=factory)

        # Second run is a no-op because data already exists
        assert await seed(json_path=json_path, session_factory=factory) == (0, 0)

        # Forced run wipes and reseeds instead of duplicating
        assert await seed(json_path=json_path, session_factory=factory, force=True) == (3, 4)
        async with factory() as session:
            scale_count = await session.scalar(select(func.count()).select_from(models.AcademicScale))
            equivalence_count = await session.scalar(
                select(func.count()).select_from(models.GradeEquivalence)
            )
            assert scale_count == 3
            assert equivalence_count == 4

        await engine.dispose()

    asyncio.run(_run())
