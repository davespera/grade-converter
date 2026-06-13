"""Seed the database from the official Spanish grade equivalences JSON.

The data source is the Resolución de 18 de septiembre de 2017 dataset
(``backend/data/equivalencias_calificaciones_espana.json``): one AcademicScale
per (country, id_escala) and one GradeEquivalence per origin grade.

Runs in two ways:
- Automatically at app startup when ``SEED_ON_STARTUP=true`` (see main.py).
- Manually: ``python -m backend.seed [--force]`` (e.g. via ``just seed``).

Seeding is idempotent: it does nothing if any scale already exists, unless
``--force`` is given, which wipes all scales and equivalences first.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import json
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, insert, select

from . import models
from .database import AsyncSessionLocal

logger = logging.getLogger(__name__)

DEFAULT_JSON_PATH = Path(__file__).resolve().parent / "data" / "equivalencias_calificaciones_espana.json"
INSERT_BATCH_SIZE = 10_000


def load_scales(json_path: Path) -> list[tuple[dict, list[dict]]]:
    """Parse the equivalences JSON into (scale, equivalences) row dicts.

    Rows use the model column names so they can be passed straight to inserts.
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    scales: list[tuple[dict, list[dict]]] = []
    for country_name, country in data["paises"].items():
        for escala in country["escalas"]:
            scale_row = {
                "country_name": country_name,
                "scale_description": escala["id_escala"],
            }
            equivalence_rows = [
                {
                    "origin_grade": origin_grade,
                    "spanish_5_10": Decimal(str(grade["equivalente_5_10"])),
                    "spanish_1_4": grade["equivalente_1_4"],
                    "spanish_literal": models.SpanishLiteralEnum(grade["equivalente_literal"]),
                }
                for origin_grade, grade in escala["calificaciones"].items()
            ]
            scales.append((scale_row, equivalence_rows))
    return scales


async def seed(
    json_path: Path = DEFAULT_JSON_PATH,
    force: bool = False,
    session_factory=AsyncSessionLocal,
) -> tuple[int, int]:
    """Seed scales and equivalences. Returns (scales, equivalences) inserted."""
    scales = load_scales(json_path)

    async with session_factory() as session:
        existing = await session.scalar(select(func.count()).select_from(models.AcademicScale))
        if existing:
            if not force:
                logger.info("Database already has %d scales, skipping seed (use --force to reseed)", existing)
                return (0, 0)
            logger.info("Force seeding: deleting %d existing scales and their equivalences", existing)
            await session.execute(delete(models.GradeEquivalence))
            await session.execute(delete(models.AcademicScale))

        total_equivalences = 0
        pending: list[dict] = []
        for scale_row, equivalence_rows in scales:
            result = await session.execute(
                insert(models.AcademicScale).values(**scale_row).returning(models.AcademicScale.id)
            )
            scale_id = result.scalar_one()
            pending.extend({**row, "scale_id": scale_id} for row in equivalence_rows)
            total_equivalences += len(equivalence_rows)
            if len(pending) >= INSERT_BATCH_SIZE:
                await session.execute(insert(models.GradeEquivalence), pending)
                pending = []
        if pending:
            await session.execute(insert(models.GradeEquivalence), pending)

        await session.commit()

    logger.info("Seeded %d scales with %d equivalences", len(scales), total_equivalences)
    return (len(scales), total_equivalences)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database from the equivalences JSON.")
    parser.add_argument("--force", action="store_true", help="Delete existing scales and reseed")
    parser.add_argument(
        "--json",
        type=Path,
        default=Path(os.getenv("SEED_JSON_PATH", DEFAULT_JSON_PATH)),
        help="Path to the equivalences JSON file",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    n_scales, n_equivalences = asyncio.run(seed(json_path=args.json, force=args.force))
    if n_scales == 0:
        print("Nothing seeded (database already populated, use --force to reseed)")
    else:
        print(f"Seeded {n_scales} scales with {n_equivalences} equivalences")


if __name__ == "__main__":
    main()
