from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas

# --- Academic Scale Operations ---

async def get_scale(db: AsyncSession, scale_id: int):
    """Fetch a specific scale and its nested equivalences."""
    query = (
        select(models.AcademicScale)
        .options(selectinload(models.AcademicScale.equivalences))
        .where(models.AcademicScale.id == scale_id)
    )

    result = await db.execute(query)
    return result.scalars().first()

async def get_scales(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Fetch all available scales for the administrative list view using pagination."""
    query = (
        # Pagination
        select(models.AcademicScale)
        .offset(skip)
        .limit(limit)
        #.options(selectinload(models.AcademicScale.equivalences))
    )

    result = await db.execute(query)
    return result.scalars().all()

async def create_scale(db: AsyncSession, scale: schemas.AcademicScaleCreate):
    """Register a new country scale."""
    new_scale = models.AcademicScale(**scale.model_dump())
    db.add(new_scale)
    await db.commit()
    await db.refresh(new_scale)
    # Ensures relationships are loaded for the response model due to async
    return await get_scale(db, new_scale.id)

# --- Grade Equivalence Operations ---

async def create_scale_equivalence(
    db: AsyncSession, equivalence: schemas.GradeEquivalenceCreate, scale_id: int
):
    """Add a specific grade mapping to an existing scale."""
    db_equivalence = models.GradeEquivalence(**equivalence.model_dump(), scale_id=scale_id)
    db.add(db_equivalence)
    await db.commit()
    await db.refresh(db_equivalence)
    return db_equivalence