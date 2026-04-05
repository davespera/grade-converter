from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, database

router = APIRouter(
    prefix="/scales",
    tags=["Academic Scales Management"]
)

@router.post("/", response_model=schemas.AcademicScale)
async def create_scale(
    scale: schemas.AcademicScaleCreate, 
    db: AsyncSession = Depends(database.get_database_session)
):
    return await crud.create_scale(db=db, scale=scale)

@router.get("/", response_model=List[schemas.AcademicScale])
async def read_scales(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(database.get_database_session)
):
    scales = await crud.get_scales(db, skip=skip, limit=limit)
    return scales

@router.get("/{scale_id}", response_model=schemas.AcademicScale)
async def read_scale(
    scale_id: int, 
    db: AsyncSession = Depends(database.get_database_session)
):
    db_scale = await crud.get_scale(db, scale_id=scale_id)
    if db_scale is None:
        raise HTTPException(status_code=404, detail="Scale not found")
    return db_scale

@router.post("/{scale_id}/equivalences/", response_model=schemas.GradeEquivalence)
async def create_equivalence_for_scale(
    scale_id: int,
    equivalence: schemas.GradeEquivalenceCreate,
    db: AsyncSession = Depends(database.get_database_session)
):
    return await crud.create_scale_equivalence(db=db, equivalence=equivalence, scale_id=scale_id)