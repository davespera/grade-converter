from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import database, models, crud
from ..auth import handle_api_key

router = APIRouter(
    prefix="/transfer",
    tags=["Transfer Logic"],
)

@router.post("/convert", response_model=models.TransferResponse, operation_id="convert_grade")
async def convert_grade(
    request: models.TransferRequest,
    db: AsyncSession = Depends(database.get_database_session),
):
    # Find the scale
    scale = await crud.get_scale(db, scale_id=request.scale_id)
    
    if not scale:
        raise HTTPException(status_code=404, detail="Academic scale not found")
    
    # Find the specific equivalence
    equivalence = await crud.get_grade_equivalence(db, request=request)
    
    if not equivalence:
        raise HTTPException(status_code=404, detail="No equivalence found for this grade")
        
    # Map DB model to Response schema
    return models.TransferResponse(
        original=equivalence.origin_grade,
        converted_5_10=equivalence.spanish_5_10,
        converted_literal=equivalence.spanish_literal.value,
    )    
