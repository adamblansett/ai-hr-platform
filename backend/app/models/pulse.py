import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Float, JSON, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class PulseSurvey(Base):
    __tablename__ = "pulse_surveys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    question = Column(String(500), nullable=False)
    category = Column(String(50), default="ENGAGEMENT") # ENGAGEMENT, BURNOUT, LEADERSHIP, WORKLOAD, INCLUSION
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    responses = relationship("PulseResponse", back_populates="survey", cascade="all, delete-orphan")


class PulseResponse(Base):
    __tablename__ = "pulse_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    survey_id = Column(String(36), ForeignKey("pulse_surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Cryptographic respondent hash to prevent duplicate voting while preserving 100% anonymity
    respondent_hash = Column(String(64), nullable=False, index=True)
    department = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False) # 1 to 5 scale or 0-10 for eNPS
    feedback_text = Column(Text, nullable=True)
    sentiment_score = Column(Float, default=0.0) # -1.0 to +1.0
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    survey = relationship("PulseSurvey", back_populates="responses")


class DepartmentSentimentScore(Base):
    __tablename__ = "department_sentiment_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    department = Column(String(100), nullable=False)
    period = Column(String(20), nullable=False) # e.g. "2026-W47"
    enps_score = Column(Float, default=0.0) # -100 to +100
    avg_rating = Column(Float, default=3.5)
    burnout_risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, ELEVATED
    total_responses = Column(Integer, default=0)
    ai_action_recommendations = Column(JSON, default=list)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
