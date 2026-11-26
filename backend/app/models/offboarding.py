import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean, JSON, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class OffboardingRecord(Base):
    __tablename__ = "offboarding_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    initiator_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    last_working_day = Column(Date, nullable=False)
    termination_reason = Column(String(50), default="VOLUNTARY_RESIGNATION") # VOLUNTARY_RESIGNATION, INVOLUNTARY_TERMINATION, RETIREMENT, CONTRACT_END
    status = Column(String(30), default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, CANCELLED
    
    scim_deprovisioned = Column(Boolean, default=False)
    equipment_returned = Column(Boolean, default=False)
    nda_reaffirmed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id])
    tasks = relationship("OffboardingTask", back_populates="offboarding", cascade="all, delete-orphan")
    exit_interview = relationship("ExitInterviewFeedback", back_populates="offboarding", uselist=False, cascade="all, delete-orphan")


class OffboardingTask(Base):
    __tablename__ = "offboarding_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offboarding_id = Column(String(36), ForeignKey("offboarding_records.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    category = Column(String(50), default="IT") # IT, HR, FINANCE, LEGAL, MANAGER
    assigned_to = Column(String(100), default="HR_ADMIN")
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    offboarding = relationship("OffboardingRecord", back_populates="tasks")


class ExitInterviewFeedback(Base):
    __tablename__ = "exit_interview_feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offboarding_id = Column(String(36), ForeignKey("offboarding_records.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    primary_reason = Column(String(100), nullable=False)
    experience_rating = Column(Integer, default=4) # 1-5 scale
    manager_feedback = Column(Text, nullable=True)
    company_culture_feedback = Column(Text, nullable=True)
    ai_synthesized_insights = Column(JSON, default=dict)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    offboarding = relationship("OffboardingRecord", back_populates="exit_interview")
