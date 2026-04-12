from __future__ import annotations 
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base

class SpanishLiteralEnum(Enum):
    APROBADO = "APROBADO"
    NOTABLE = "NOTABLE"
    SOBRESALIENTE = "SOBRESALIENTE"
    MATRICULA = "MATRICULA"

class AcademicScale(Base):
    __tablename__ = "academic_scales"
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False)
    scale_description = Column(String(255), nullable=False)
    total_grades = Column(Integer)
    
    #__table_args__ = (UniqueConstraint('country_name', 'scale_description', name='_country_scale_uc'),)
    # Check whether lazy="selectin" is needed to avoid queries outside async IO (probably yes if option removed from crud.py)
    equivalences = relationship("GradeEquivalence", back_populates="scale", lazy="selectin")

class GradeEquivalence(Base):
    __tablename__ = "grade_equivalences"
    
    id = Column(Integer, primary_key=True, index=True)
    scale_id = Column(Integer, ForeignKey("academic_scales.id", ondelete="CASCADE"))
    origin_grade = Column(String(50), nullable=False)
    spanish_5_10 = Column(Numeric(4, 2), nullable=False)
    spanish_1_4 = Column(Integer, nullable=True)
    spanish_literal = Column(SQLEnum(SpanishLiteralEnum), nullable=False)
    
    scale = relationship("AcademicScale", back_populates="equivalences")

# One To One relationship
