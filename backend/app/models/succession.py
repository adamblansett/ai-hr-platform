import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class SkillCompetency(Base):
    __tablename__ = "skill_competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="TECHNICAL")  # TECHNICAL, LEADERSHIP, DOMAIN, COMPLIANCE
    proficiency_level = Column(Integer, default=3)  # 1 to 5 scale
    verified_by_manager = Column(Boolean, default=False)
    last_assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", foreign_keys=[employee_id])


class FlightRiskAssessment(Base):
    __tablename__ = "flight_risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    risk_score = Column(Float, nullable=False)  # 0.00 to 1.00
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    contributing_factors = Column(JSON, default=list)  # ["Tenure in role > 3 yrs", "Market comp ratio < 0.85"]
    recommended_interventions = Column(JSON, default=list)  # ["Conduct compensation review", "Assign stretch project"]
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", foreign_keys=[employee_id])


class InternalRequisition(Base):
    __tablename__ = "internal_requisitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    min_experience_years = Column(Integer, default=2)
    required_skills = Column(JSON, default=list)  # ["Python", "FastAPI", "Distributed Systems"]
    target_headcount = Column(Integer, default=1)
    status = Column(String(20), default="OPEN")  # OPEN, INTERVIEWING, FILLED, CLOSED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
