#from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from . import models

# --- Academic Scale Operations ---

async def get_scale(db: AsyncSession, scale_id: int):
    """Fetch a specific scale and its nested equivalences."""
    query = (
        select(models.AcademicScale)
        #.options(selectinload(models.AcademicScale.equivalences))
        .where(models.AcademicScale.id == scale_id)
    )

    result = await db.exec(query)
    return result.first()

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
    new_scale = models.AcademicScale(**scale.model_dump())
    db.add(new_scale)
    await db.commit()
    await db.refresh(new_scale)
    # Ensures relationships are loaded for the response model due to async
    return await get_scale(db, new_scale.id)

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

async def get_grade_equivalence(db: AsyncSession, request: models.TransferRequest):
    query = (
        select(models.GradeEquivalence).where(
            models.GradeEquivalence.scale_id == request.scale_id,
            models.GradeEquivalence.origin_grade == request.origin_grade,
        )
    )

    result = await db.exec(query)
    return result.first()