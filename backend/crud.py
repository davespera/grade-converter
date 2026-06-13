from sqlalchemy.orm import noload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from . import models


def normalize_grade(grade: str) -> str:
    """Round a grade string to 2 decimal places, comma as decimal separator.

    Non-numeric grades (letter grades, codes) are returned unchanged so they
    still participate in exact matching against letter-grade scales.
    """
    try:
        return f"{round(float(grade.replace(',', '.')), 2):.2f}".replace('.', ',')
    except ValueError:
        return grade


# --- Academic Scale Operations ---

async def get_scale(db: AsyncSession, scale_id: int):
    """Fetch a specific scale and its nested equivalences."""
    db_scale = await db.get(models.AcademicScale, scale_id)
    return db_scale

async def get_scales(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Fetch all available scales for the administrative list view using pagination."""
    query = (
        select(models.AcademicScale)
        .offset(skip)
        .limit(limit)
    )

    result = await db.exec(query)
    return result.all()

async def search_scales(
    db: AsyncSession,
    country: str | None = None,
    scale_description: str | None = None,
    skip: int = 0,
    limit: int = 20,
):
    """List scales filtered by country and/or scale identifier (id_escala).

    Both filters are case-insensitive substring matches. Equivalences are not
    loaded (noload overrides the relationship's selectin eager loading), keeping
    this a lightweight list for country/scale lookups.
    """
    query = select(models.AcademicScale).options(
        noload(models.AcademicScale.equivalences)
    )
    if country:
        query = query.where(models.AcademicScale.country_name.ilike(f"%{country}%"))
    if scale_description:
        query = query.where(models.AcademicScale.scale_description.ilike(f"%{scale_description}%"))
    query = query.offset(skip).limit(limit)

    result = await db.exec(query)
    return result.all()

async def match_scales(
    db: AsyncSession,
    country: str,
    grades: list[str],
) -> list[models.ScaleMatchResult]:
    """Rank a country's scales by how many of the given grades they cover.

    The transcript's grade set is the only signal that disambiguates between the
    many scales a country can have (their ``scale_description`` / id_escala is an
    opaque code that cannot be derived from a transcript). For each scale under the
    country we count how many distinct query grades have an equivalence, and rank by
    coverage. Equivalences load via the relationship's default selectin eager loading.
    """
    query_set = {normalize_grade(g) for g in grades}

    query = select(models.AcademicScale).where(
        models.AcademicScale.country_name.ilike(f"%{country}%")
    )
    result = await db.exec(query)
    scales = result.all()

    results: list[models.ScaleMatchResult] = []
    for scale in scales:
        scale_grades = {e.origin_grade for e in scale.equivalences}
        matched = query_set & scale_grades
        results.append(
            models.ScaleMatchResult(
                scale_id=scale.id,
                country_name=scale.country_name,
                scale_description=scale.scale_description,
                matched_count=len(matched),
                total_query_grades=len(query_set),
                scale_total_grades=len(scale_grades),
                unmatched_grades=sorted(query_set - scale_grades),
                coverage=len(matched) / len(query_set) if query_set else 0.0,
            )
        )

    # Highest coverage first, then the tightest scale, then a deterministic id.
    results.sort(key=lambda r: (-r.coverage, r.scale_total_grades, r.scale_id))
    return results


async def create_scale(db: AsyncSession, scale: models.AcademicScaleCreate):
    """Register a new country scale."""
    db_scale = models.AcademicScale.model_validate(scale)
    db.add(db_scale)
    await db.commit()
    await db.refresh(db_scale)
    return db_scale

async def delete_scale(db: AsyncSession, scale_id: int) -> bool:
    """Delete an existing scale."""
    scale = await db.get(models.AcademicScale, scale_id)
    if not scale:
        return False
    await db.delete(scale)
    await db.commit()
    return True

async def update_scale(db: AsyncSession, scale_id: int, scale: models.AcademicScaleUpdate):
    """Update all or some values of an existing scale."""
    db_scale = await db.get(models.AcademicScale, scale_id)
    scale_data = scale.model_dump(exclude_unset=True)
    db_scale.sqlmodel_update(scale_data)
    db.add(db_scale)
    await db.commit()
    await db.refresh(db_scale)
    return db_scale

# --- Grade Equivalence Operations ---

async def create_grade_equivalence(
    db: AsyncSession, equivalence: models.GradeEquivalenceCreate, scale_id: int
):
    """Add a specific grade mapping to an existing scale."""
    db_equivalence = models.GradeEquivalence(**equivalence.model_dump(), scale_id=scale_id)
    db.add(db_equivalence)
    await db.commit()
    await db.refresh(db_equivalence)
    return db_equivalence

async def get_grade_equivalence(db: AsyncSession, scale_id: int, origin_grade: str):
    query = (
        select(models.GradeEquivalence).where(
            models.GradeEquivalence.scale_id == scale_id,
            models.GradeEquivalence.origin_grade == origin_grade,
        )
    )
    result = await db.exec(query)
    return result.first()

async def delete_equivalence(db: AsyncSession, scale_id: int, equivalence_id: int) -> bool:
    """Delete a specific grade mapping in an existing scale."""
    equivalence = await db.get(models.GradeEquivalence, equivalence_id)
    if not equivalence or equivalence.scale_id != scale_id:
        return False
    await db.delete(equivalence)
    await db.commit()
    return True

async def update_equivalence(db: AsyncSession, equivalence_id: int, equivalence: models.GradeEquivalenceUpdate):
    """Update all or some values of a specific grade mapping in an existing scale."""
    db_equivalence = await db.get(models.GradeEquivalence, equivalence_id)
    equivalence_data = equivalence.model_dump(exclude_unset=True)
    db_equivalence.sqlmodel_update(equivalence_data)
    db.add(db_equivalence)
    await db.commit()
    await db.refresh(db_equivalence)
    return db_equivalence