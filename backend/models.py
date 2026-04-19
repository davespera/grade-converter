from enum import Enum
from decimal import Decimal

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel

class SpanishLiteralEnum(str, Enum):
    APROBADO = "APROBADO"
    NOTABLE = "NOTABLE"
    SOBRESALIENTE = "SOBRESALIENTE"
    MATRICULA = "MATRICULA"

class AcademicScale(SQLModel, table=True):
    __tablename__ = "academic_scales"
    id: int | None = Field(default=None, primary_key=True, index=True)
    country_name: str = Field(max_length=100)
    scale_description: str = Field(max_length=255)
    total_grades: int | None = None

    equivalences: list["GradeEquivalence"] = Relationship(
        back_populates="scale",
        # Use eager, in this case selectin, loading to avoid errors with async sessions
        # Better to do 2 queries, as for a single scale there might be several equivalences
        sa_relationship_kwargs={"lazy": "selectin"}, 
    )

class GradeEquivalence(SQLModel, table=True):
    __tablename__ = "grade_equivalences"

    id: int | None = Field(default=None, primary_key=True, index=True)
    scale_id: int | None = Field(default=None, foreign_key="academic_scales.id")
    origin_grade: str = Field(max_length=50)
    spanish_5_10: Decimal = Field(max_digits=4, decimal_places=2)
    spanish_1_4: int | None = Field(default=None)
    spanish_literal: SpanishLiteralEnum

    scale: AcademicScale | None = Relationship(
        back_populates="equivalences",
        # Use joined loading to ensure the scale is loaded with the equivalence for response models
        # Many-to-one relationship, so joined loading is better as for each equivalence value there will be a single scale value
        sa_relationship_kwargs={"lazy": "joined"},
    )

# --- Shared API Schemas ---

class GradeEquivalenceBase(SQLModel):
    origin_grade: str = Field(description="Grade from origin country")
    spanish_5_10: float = Field(ge=5.0, le=10.0)
    spanish_1_4: int | None = Field(default=None, ge=1, le=4)
    spanish_literal: SpanishLiteralEnum


class GradeEquivalenceCreate(GradeEquivalenceBase):
    pass


class GradeEquivalenceRead(GradeEquivalenceBase):
    id: int
    scale_id: int

    model_config = ConfigDict(from_attributes=True)


class AcademicScaleBase(SQLModel):
    country_name: str
    scale_description: str
    total_grades: int | None = None


class AcademicScaleCreate(AcademicScaleBase):
    pass


class AcademicScaleList(AcademicScaleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AcademicScaleRead(AcademicScaleBase):
    id: int
    equivalences: list[GradeEquivalenceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TransferRequest(SQLModel):
    """Schema for the Activepieces automation request"""

    scale_id: int
    origin_grade: str


class TransferResponse(SQLModel):
    """The clean data sent back to the automation flow"""

    original: str
    converted_5_10: Decimal
    converted_literal: str

    model_config = ConfigDict(from_attributes=True)
