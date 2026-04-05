from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/transfer", tags=["Transfer Logic"])

@router.post("/convert", response_model=schemas.TransferResponse)
def convert_grade(request: schemas.TransferRequest, db: Session = Depends(database.get_database_session)):
    # Find the scale
    scale = db.select(models.AcademicScale).where(
        models.AcademicScale.id == request.scale_id
    ).first()
    
    if not scale:
        raise HTTPException(status_code=404, detail="Academic scale not found")
    
    # Find the specific equivalence
    equivalence = db.select(models.GradeEquivalence).where(
        models.GradeEquivalence.scale_id == request.scale_id,
        models.GradeEquivalence.origin_grade == request.origin_grade
    ).first()
    
    if not equivalence:
        raise HTTPException(status_code=404, detail="No equivalence found for this grade")
        
    # Map DB model to Response schema
    return schemas.TransferResponse(
        original=result.origin_grade,
        converted_5_10=result.spanish_5_10,
        converted_literal=result.spanish_literal
    )    
