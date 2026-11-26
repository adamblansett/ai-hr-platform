import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    TEAMS = "TEAMS"
    IN_APP = "IN_APP"


class NotificationCategory(str, Enum):
    LEAVE_APPROVAL = "LEAVE_APPROVAL"
    VISA_EXPIRY = "VISA_EXPIRY"
    COMPLIANCE_LMS = "COMPLIANCE_LMS"
    REVIEW_DEADLINE = "REVIEW_DEADLINE"
    ONBOARDING_REMINDER = "ONBOARDING_REMINDER"
    SECURITY_ALERT = "SECURITY_ALERT"


class NotificationStatus(str, Enum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"


class NotificationDispatch(Base):
    """Multi-channel notification & HR digest audit log."""
    __tablename__ = "notification_dispatches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=NotificationStatus.QUEUED.value, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
