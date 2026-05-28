from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import crud, database, models
from ..auth import handle_api_key

router = APIRouter(
    prefix="/scales",
    tags=["Academic Scales Management"],
)

@router.post("/", response_model=models.AcademicScaleRead, operation_id="create_scale")
async def create_scale(
    scale: models.AcademicScaleCreate, 
    db: AsyncSession = Depends(database.get_database_session)
):
    return await crud.create_scale(db=db, scale=scale)

@router.get("/", response_model=List[models.AcademicScaleRead], operation_id="read_scales")
async def read_scales(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(database.get_database_session)
):
    scales = await crud.get_scales(db, skip=skip, limit=limit)
    return scales

@router.get("/{scale_id}", response_model=models.AcademicScaleRead, operation_id="read_scale")
async def read_scale(
    scale_id: int, 
    db: AsyncSession = Depends(database.get_database_session)
):
    db_scale = await crud.get_scale(db, scale_id=scale_id)
    if db_scale is None:
        raise HTTPException(status_code=404, detail="Scale not found")
    return db_scale

@router.delete("/{scale_id}", operation_id="delete_scale")
async def delete_grade_equivalence(
    scale_id: int,
    db: AsyncSession = Depends(database.get_database_session)
):
    """Delete a specific grade mapping in an existing scale."""
    
    scale = await db.get(models.AcademicScale, scale_id)
    if not scale:
        raise HTTPException(status_code=404, detail="Scale not found")
    await db.delete(scale)
    await db.commit()
    return {"OK": True}

@router.post("/{scale_id}/equivalences/", response_model=models.GradeEquivalenceRead, operation_id="create_equivalence_for_scale")
async def create_equivalence_for_scale(
    scale_id: int,
    equivalence: models.GradeEquivalenceCreate,
    db: AsyncSession = Depends(database.get_database_session)
):
    return await crud.create_grade_equivalence(db=db, equivalence=equivalence, scale_id=scale_id)

@router.delete("/{scale_id}/equivalences/{equivalence_id}", operation_id="delete_equivalence_for_scale")
async def delete_grade_equivalence(
    equivalence_id: int, 
    scale_id: int,
    db: AsyncSession = Depends(database.get_database_session)
):
    """Delete a specific grade mapping in an existing scale."""
    
    equivalence = await db.get(models.GradeEquivalence, equivalence_id) # {"id": equivalence_id, "scale_id": scale_id}
    if not equivalence or equivalence.scale_id != scale_id:
        raise HTTPException(status_code=404, detail="Equivalence not found")
    await db.delete(equivalence)
    await db.commit()
    return {"OK": True}