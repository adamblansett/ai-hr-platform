import enum
import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Date, Float, Integer, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class PayFrequency(str, enum.Enum):
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    SEMI_MONTHLY = "SEMI_MONTHLY"
    MONTHLY = "MONTHLY"

class EquityGrantType(str, enum.Enum):
    RSU = "RSU"
    ISO = "ISO"
    NSO = "NSO"
    SAR = "SAR"

class CompensationPackage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "compensation_packages"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    pay_frequency: Mapped[PayFrequency] = mapped_column(
        Enum(PayFrequency), default=PayFrequency.BI_WEEKLY, nullable=False
    )
    target_bonus_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")

class EquityGrant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "equity_grants"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    grant_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    grant_type: Mapped[EquityGrantType] = mapped_column(
        Enum(EquityGrantType), default=EquityGrantType.RSU, nullable=False
    )
    total_shares: Mapped[int] = mapped_column(Integer, nullable=False)
    strike_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    grant_date: Mapped[date] = mapped_column(Date, nullable=False)
    vesting_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    cliff_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    vesting_duration_months: Mapped[int] = mapped_column(Integer, default=48, nullable=False)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")

class PaystubRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "paystub_records"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    pay_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    pay_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    pay_date: Mapped[date] = mapped_column(Date, nullable=False)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_withholdings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    benefit_deductions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
