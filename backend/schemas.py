from __future__ import annotations 
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# --- Grade Equivalence Schemas ---

# Define the allowed literals
class SpanishLiteral(str, Enum):
    APROBADO = "APROBADO"
    NOTABLE = "NOTABLE"
    SOBRESALIENTE = "SOBRESALIENTE"
    MATRICULA = "MATRICULA"

class GradeEquivalenceBase(BaseModel):
    origin_grade: str = Field(..., description="Grade from origin country")
    spanish_5_10: float = Field(..., ge=5.0, le=10.0)
    # Optional[int] with a default of None
    spanish_1_4: Optional[int] = Field(None, ge=1, le=4)
    spanish_literal: SpanishLiteral

class GradeEquivalenceCreate(GradeEquivalenceBase):
    pass  # Used for POST requests to add new equivalences

class GradeEquivalence(GradeEquivalenceBase):
    id: int
    scale_id: int

    model_config = ConfigDict(from_attributes=True) # Allows Pydantic to read SQLAlchemy objects

# --- Academic Scale Schemas ---

class AcademicScaleBase(BaseModel):
    country_name: str
    scale_description: str
    total_grades: Optional[int] = None

class AcademicScaleCreate(AcademicScaleBase):
    pass

# Scales without equivalences
class AcademicScaleList(AcademicScaleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AcademicScale(AcademicScaleBase):
    id: int
    # This allows to nest the equivalences inside the scale object if needed
    equivalences: List[GradeEquivalence] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

# --- Logic-Specific Schemas ---

class TransferRequest(BaseModel):
    """Schema for the Activepieces automation request"""
    scale_id: int
    origin_grade: str

class TransferResponse(BaseModel):
    """The clean data sent back to the automation flow"""
    original: str
    converted_5_10: Decimal
    converted_literal: str
    
    model_config = ConfigDict(from_attributes=True)
