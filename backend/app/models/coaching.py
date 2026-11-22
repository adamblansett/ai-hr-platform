import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean, JSON, Integer, Float, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class OneOnOneMeeting(Base):
    __tablename__ = "one_on_one_meetings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    manager_id = Column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    scheduled_date = Column(Date, nullable=False)
    status = Column(String(20), default="SCHEDULED") # SCHEDULED, COMPLETED, CANCELLED
    talking_points = Column(JSON, default=list) # ["OKR Review", "Career Progression", "Blockers"]
    ai_suggested_prompts = Column(JSON, default=list)
    manager_notes = Column(Text, nullable=True)
    action_items = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    manager = relationship("Employee", foreign_keys=[manager_id])
    employee = relationship("Employee", foreign_keys=[employee_id])


class CalibrationSession(Base):
    __tablename__ = "calibration_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    cycle_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    total_reviewed = Column(Integer, default=0)
    rating_distribution = Column(JSON, default=dict) # {"1": 2, "2": 5, "3": 18, "4": 8, "5": 2}
    detected_biases = Column(JSON, default=list) # ["CENTRAL_TENDENCY_BIAS", "LENIENCY_BIAS"]
    recommendations = Column(JSON, default=list)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
