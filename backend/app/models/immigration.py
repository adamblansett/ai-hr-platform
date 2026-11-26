import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class VisaType(str, Enum):
    H1B = "H1B"
    L1A_MANAGER = "L1A"
    L1B_SPECIALIZED = "L1B"
    O1_EXTRAORDINARY = "O1"
    TN_USMCA = "TN"
    PERM_GREEN_CARD = "PERM_GREEN_CARD"
    SCHENGEN_BLUE_CARD = "SCHENGEN_BLUE_CARD"


class CaseStatus(str, Enum):
    INTAKE = "INTAKE"
    DRAFTING = "DRAFTING"
    DOL_PREVAILING_WAGE = "DOL_PREVAILING_WAGE"
    USCIS_SUBMITTED = "USCIS_SUBMITTED"
    RFE_ISSUED = "RFE_ISSUED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    I94_ARRIVAL = "I94"
    DIPLOMA = "DIPLOMA"
    TRANSCRIPT = "TRANSCRIPT"
    LCA_CERTIFICATION = "LCA"
    USCIS_APPROVAL_NOTICE = "I797_APPROVAL"
    OTHER = "OTHER"


class ImmigrationCase(Base):
    __tablename__ = "immigration_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    visa_type: Mapped[str] = mapped_column(String(30), default=VisaType.H1B.value)
    case_status: Mapped[str] = mapped_column(String(30), default=CaseStatus.INTAKE.value)
    uscis_receipt_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uscis_center: Mapped[Optional[str]] = mapped_column(String(50), default="California Service Center (WAC)")
    filing_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    expiry_date: Mapped[str] = mapped_column(String(10), nullable=False)
    assigned_attorney: Mapped[str] = mapped_column(String(100), default="Fragomen, Del Rey, Bernsen & Loewy, LLP")
    
    # Global Relocation & Tax Gross-Up
    relocation_stipend_amount: Mapped[float] = mapped_column(Float, default=10000.0)
    stipend_disbursed: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_gross_up_amount: Mapped[float] = mapped_column(Float, default=3200.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    documents: Mapped[List["ImmigrationDocument"]] = relationship("ImmigrationDocument", back_populates="case", cascade="all, delete-orphan")


class ImmigrationDocument(Base):
    __tablename__ = "immigration_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("immigration_cases.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(30), default=DocumentType.PASSPORT.value)
    document_name: Mapped[str] = mapped_column(String(150), nullable=False)
    document_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["ImmigrationCase"] = relationship("ImmigrationCase", back_populates="documents")
