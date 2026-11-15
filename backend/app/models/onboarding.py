import enum
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Date, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class OnboardingCategory(str, enum.Enum):
    DOCUMENTATION = "DOCUMENTATION"
    EQUIPMENT = "EQUIPMENT"
    ACCESS_PROVISIONING = "ACCESS_PROVISIONING"
    TRAINING = "TRAINING"
    COMPLIANCE = "COMPLIANCE"

class OnboardingStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    WAIVED = "WAIVED"

class OnboardingTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "onboarding_tasks"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    # Traceability back to upstream recruitment handoff
    recruiter_candidate_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    offer_acceptance_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[OnboardingCategory] = mapped_column(
        Enum(OnboardingCategory), default=OnboardingCategory.DOCUMENTATION, nullable=False
    )
    status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus), default=OnboardingStatus.PENDING, index=True, nullable=False
    )
    
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    assigned_to_role: Mapped[str] = mapped_column(String(50), default="EMPLOYEE", nullable=False) # e.g. EMPLOYEE, HR_ADMIN, IT_ADMIN
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    external_system_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False) # e.g. Okta / Google Workspace provisioning details

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="onboarding_tasks", foreign_keys=[employee_id])
