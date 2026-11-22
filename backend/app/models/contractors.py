from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class TaxFormType(str, Enum):
    W9 = "W9"
    W8_BEN = "W8_BEN"
    W8_BEN_E = "W8_BEN_E"
    VAT_REGISTRATION = "VAT_REGISTRATION"


class ContractorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ONBOARDING = "ONBOARDING"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"


class ContractorProfile(Base):
    __tablename__ = "contractor_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), default="INDIVIDUAL")
    tax_form_type: Mapped[str] = mapped_column(String(30), default=TaxFormType.W8_BEN.value)
    tax_form_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_id_masked: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hourly_rate: Mapped[float] = mapped_column(Float, default=75.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(30), default=ContractorStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sows: Mapped[List["ContractorSOW"]] = relationship("ContractorSOW", back_populates="contractor", cascade="all, delete-orphan")


class ContractorSOW(Base):
    __tablename__ = "contractor_sows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    contractor_id: Mapped[str] = mapped_column(String(36), ForeignKey("contractor_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    total_budget: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    deliverables_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contractor: Mapped["ContractorProfile"] = relationship("ContractorProfile", back_populates="sows")
    invoices: Mapped[List["MilestoneInvoice"]] = relationship("MilestoneInvoice", back_populates="sow", cascade="all, delete-orphan")


class MilestoneInvoice(Base):
    __tablename__ = "milestone_invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sow_id: Mapped[str] = mapped_column(String(36), ForeignKey("contractor_sows.id"), nullable=False)
    contractor_id: Mapped[str] = mapped_column(String(36), ForeignKey("contractor_profiles.id"), nullable=False)
    milestone_title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(30), default=InvoiceStatus.SUBMITTED.value)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    payout_tx_hash: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    sow: Mapped["ContractorSOW"] = relationship("ContractorSOW", back_populates="invoices")
