#from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from . import models

# --- Academic Scale Operations ---

async def get_scale(db: AsyncSession, scale_id: int):
    """Fetch a specific scale and its nested equivalences."""
    scale = await db.get(models.AcademicScale, scale_id)
    return scale

async def get_scales(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Fetch all available scales for the administrative list view using pagination."""
    query = (
        select(models.AcademicScale)
        #.options(selectinload(models.AcademicScale.equivalences))
        .offset(skip)
        .limit(limit)
    )

    result = await db.exec(query)
    return result.all()

async def create_scale(db: AsyncSession, scale: models.AcademicScaleCreate):
    """Register a new country scale."""
    db_scale = models.AcademicScale.model_validate(scale)
    db.add(db_scale)
    await db.commit()
    await db.refresh(db_scale)
    # Ensures relationships are loaded for the response model due to async
    return await get_scale(db, db_scale.id)

async def delete_scale(db: AsyncSession, scale_id: int) -> bool:
    """Delete an existing scale."""
    scale = await db.get(models.AcademicScale, scale_id)
    if not scale:
        return False
    await db.delete(scale)
    await db.commit()
    return True

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