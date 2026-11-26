import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class IncidentType(str, Enum):
    INJURY = "INJURY"
    ILLNESS = "ILLNESS"
    NEAR_MISS = "NEAR_MISS"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    PROPERTY_DAMAGE = "PROPERTY_DAMAGE"


class IncidentSeverity(str, Enum):
    FIRST_AID = "FIRST_AID"
    MEDICAL_TREATMENT = "MEDICAL_TREATMENT"
    RESTRICTED_DUTY = "RESTRICTED_DUTY"
    DAYS_AWAY = "DAYS_AWAY"
    FATALITY = "FATALITY"


class IncidentStatus(str, Enum):
    REPORTED = "REPORTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CORRECTIVE_ACTIONS_PENDING = "CORRECTIVE_ACTIONS_PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class SafetyIncident(Base):
    __tablename__ = "safety_incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    incident_type: Mapped[str] = mapped_column(String(30), default=IncidentType.INJURY.value)
    severity: Mapped[str] = mapped_column(String(30), default=IncidentSeverity.FIRST_AID.value)
    incident_date: Mapped[str] = mapped_column(String(10), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # OSHA Compliance Specifics
    is_osha_recordable: Mapped[bool] = mapped_column(Boolean, default=False)
    osha_case_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lost_workday_count: Mapped[int] = mapped_column(Integer, default=0)
    restricted_days_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # AI Root-Cause & Corrective Actions
    ai_root_cause_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=IncidentStatus.REPORTED.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
