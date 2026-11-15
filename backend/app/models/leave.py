import enum
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Date, Float, Enum, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class LeaveType(str, enum.Enum):
    PTO = "PTO"
    SICK = "SICK"
    PARENTAL = "PARENTAL"
    BEREAVEMENT = "BEREAVEMENT"
    UNPAID = "UNPAID"

class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class LeavePolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leave_policies"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    leave_type: Mapped[LeaveType] = mapped_column(Enum(LeaveType), nullable=False)
    annual_days_allowed: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    accrual_rate_per_month: Mapped[float] = mapped_column(Float, default=1.25, nullable=False)
    max_carryover_days: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class LeaveBalance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leave_balances"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leave_policies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    accrued_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    used_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carried_over_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    @property
    def remaining_days(self) -> float:
        return self.accrued_days + self.carried_over_days - self.used_days

class LeaveRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leave_requests"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leave_policies.id", ondelete="RESTRICT"), nullable=False
    )
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus), default=LeaveStatus.PENDING, index=True, nullable=False
    )
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calendar_conflict_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="leave_requests", foreign_keys=[employee_id]
    )
    policy: Mapped["LeavePolicy"] = relationship("LeavePolicy")
    approver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[approver_id])
