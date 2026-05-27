from enum import Enum
from decimal import Decimal
from datetime import datetime, timezone

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel

# --- Shared API Schemas ---

class GradeEquivalenceBase(SQLModel):
    origin_grade: str = Field(description="Grade from origin country")
    spanish_5_10: Decimal = Field(max_digits=4, decimal_places=2)
    spanish_1_4: int | None = Field(default=None) # Maybe add ge=1, le=4
    spanish_literal: SpanishLiteralEnum


class GradeEquivalenceCreate(GradeEquivalenceBase):
    pass


class GradeEquivalenceRead(GradeEquivalenceBase):
    id: int
    scale_id: int

    model_config = ConfigDict(from_attributes=True)


class AcademicScaleBase(SQLModel):
    country_name: str = Field(max_length=100)
    scale_description: str = Field(max_length=255)
    total_grades: int | None = None # Defaults to None


class AcademicScaleCreate(AcademicScaleBase):
    pass


class AcademicScaleList(AcademicScaleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AcademicScaleRead(AcademicScaleBase):
    id: int
    equivalences: list[GradeEquivalenceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GradeInput(SQLModel):
    """Schema for the grade to be converted"""

    subject: str | None = None
    origin_grade: str

class TransferRequest(SQLModel):
    """Schema for the transfer request"""

    scale_id: int
    grades: list[GradeInput]

class GradeOutput(SQLModel):
    """Schema for the converted grade"""

    subject: str | None = None
    origin_grade: str
    converted_5_10: Decimal
    converted_literal: str

    model_config = ConfigDict(from_attributes=True)

class TransferResponse(SQLModel):
    """The clean data sent back"""

    conversion: list[GradeOutput]

# --- Tables ---

class SpanishLiteralEnum(str, Enum):
    APROBADO = "APROBADO"
    NOTABLE = "NOTABLE"
    SOBRESALIENTE = "SOBRESALIENTE"
    MATRICULA = "MATRICULA"

class AcademicScale(AcademicScaleBase, table=True):
    __tablename__ = "academic_scales"
    id: int | None = Field(default=None, primary_key=True, index=True)

    equivalences: list["GradeEquivalence"] = Relationship(
        back_populates="scale",
        # Use eager, in this case selectin, loading to avoid errors with async sessions
        # Better to do 2 queries, as for a single scale there might be several equivalences
        sa_relationship_kwargs={"lazy": "selectin"}, 
    )

class GradeEquivalence(GradeEquivalenceBase, table=True):
    __tablename__ = "grade_equivalences"

    id: int | None = Field(default=None, primary_key=True, index=True)
    scale_id: int | None = Field(default=None, foreign_key="academic_scales.id")

    scale: AcademicScale | None = Relationship(
        back_populates="equivalences",
        # Use joined loading to ensure the scale is loaded with the equivalence for response models
        # Many-to-one relationship, so joined loading is better as for each equivalence value there will be a single scale value
        sa_relationship_kwargs={"lazy": "joined"},
    )

# --- API Authentication ---

class ApiUserBase(SQLModel):
    active: bool = Field(..., description="Whether the user is active or not")
    api_key: str = Field(..., description="The API key for the user", unique=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The date and time the user was created",
    )
    is_internal: bool = Field(..., description="Whether the user is internal or not")


class ApiUser(ApiUserBase, table=True):
    __tablename__ = "api_users"

    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(default="service", max_length=100)
