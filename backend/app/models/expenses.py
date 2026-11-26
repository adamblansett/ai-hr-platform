import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class ExpenseCategory(str, Enum):
    MEALS = "MEALS"
    TRAVEL = "TRAVEL"
    LODGING = "LODGING"
    SOFTWARE = "SOFTWARE"
    OFFICE_SUPPLIES = "OFFICE_SUPPLIES"
    OTHER = "OTHER"


class ExpenseStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REIMBURSED = "REIMBURSED"


class AuditStatus(str, Enum):
    PENDING = "PENDING"
    COMPLIANT = "COMPLIANT"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"


class ExpenseReport(Base):
    __tablename__ = "expense_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=ExpenseStatus.DRAFT.value)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    audit_status: Mapped[str] = mapped_column(String(30), default=AuditStatus.PENDING.value)
    audit_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reimbursement_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    items: Mapped[List["ExpenseItem"]] = relationship("ExpenseItem", back_populates="report", cascade="all, delete-orphan")


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("expense_reports.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    expense_date: Mapped[str] = mapped_column(String(10), nullable=False)
    merchant: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_compliant: Mapped[bool] = mapped_column(Boolean, default=True)
    policy_flags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    report: Mapped["ExpenseReport"] = relationship("ExpenseReport", back_populates="items")
