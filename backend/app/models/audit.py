import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. "Employee", "LeaveRequest", "Policy"
    entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pii_redacted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="audit_logs")
    actor: Mapped[Optional["Employee"]] = relationship("Employee")
