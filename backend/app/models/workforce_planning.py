import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from sqlalchemy import String, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class RecruiterSyncStatus(str, Enum):
    PENDING = "PENDING"
    SYNCED_TO_RECRUITER = "SYNCED_TO_RECRUITER"
    FILLED = "FILLED"


class WorkforcePlan(Base):
    """Departmental headcount plan & attrition/budget forecast."""
    __tablename__ = "workforce_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    current_headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    target_headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    approved_budget_usd: Mapped[float] = mapped_column(Float, nullable=False)
    projected_attrition_rate: Mapped[float] = mapped_column(Float, default=0.08, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PlanStatus.DRAFT.value, nullable=False)
    ai_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False)

    requisitions: Mapped[List["HeadcountRequisitionForecast"]] = relationship(
        "HeadcountRequisitionForecast", back_populates="plan", cascade="all, delete-orphan"
    )


class HeadcountRequisitionForecast(Base):
    """Planned headcount requisition synced to ai-recruiter."""
    __tablename__ = "headcount_requisition_forecasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workforce_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    job_level: Mapped[str] = mapped_column(String(30), nullable=False)
    target_quarter: Mapped[str] = mapped_column(String(10), nullable=False)
    estimated_base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    fully_loaded_cost: Mapped[float] = mapped_column(Float, nullable=False)
    recruiter_sync_status: Mapped[str] = mapped_column(
        String(30), default=RecruiterSyncStatus.PENDING.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)

    plan: Mapped["WorkforcePlan"] = relationship("WorkforcePlan", back_populates="requisitions")
