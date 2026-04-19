from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import database, models

router = APIRouter(prefix="/transfer", tags=["Transfer Logic"])

@router.post("/convert", response_model=models.TransferResponse)
async def convert_grade(
    request: models.TransferRequest,
    db: AsyncSession = Depends(database.get_database_session),
):
    # Find the scale
    scale_result = await db.exec(
        select(models.AcademicScale).where(models.AcademicScale.id == request.scale_id)
    )
    scale = scale_result.first()
    
    if not scale:
        raise HTTPException(status_code=404, detail="Academic scale not found")
    
    # Find the specific equivalence
    equivalence_result = await db.exec(
        select(models.GradeEquivalence).where(
            models.GradeEquivalence.scale_id == request.scale_id,
            models.GradeEquivalence.origin_grade == request.origin_grade,
        )
    )
    equivalence = equivalence_result.first()
    
    if not equivalence:
        raise HTTPException(status_code=404, detail="No equivalence found for this grade")
        
    # Map DB model to Response schema
    return models.TransferResponse(
        original=equivalence.origin_grade,
        converted_5_10=equivalence.spanish_5_10,
        converted_literal=equivalence.spanish_literal.value,
    )    
