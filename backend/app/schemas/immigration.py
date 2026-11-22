from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ImmigrationCaseCreate(BaseModel):
    employee_id: str
    visa_type: str = Field(..., description="H1B, L1A, L1B, O1, TN, PERM_GREEN_CARD, SCHENGEN_BLUE_CARD")
    expiry_date: str = Field(..., description="YYYY-MM-DD")
    uscis_receipt_number: Optional[str] = None
    uscis_center: Optional[str] = "California Service Center (WAC)"
    filing_date: Optional[str] = None
    assigned_attorney: Optional[str] = "Fragomen, Del Rey, Bernsen & Loewy, LLP"
    relocation_stipend_amount: float = 10000.0


class ImmigrationDocumentResponse(BaseModel):
    id: str
    case_id: str
    document_type: str
    document_name: str
    document_url: str
    is_verified: bool
    uploaded_at: datetime


class ImmigrationCaseResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    visa_type: str
    case_status: str
    uscis_receipt_number: Optional[str] = None
    uscis_center: Optional[str] = None
    filing_date: Optional[str] = None
    expiry_date: str
    assigned_attorney: str
    relocation_stipend_amount: float
    stipend_disbursed: bool
    tax_gross_up_amount: float
    created_at: datetime
    documents: List[ImmigrationDocumentResponse] = []


class CaseStatusUpdateRequest(BaseModel):
    new_status: str = Field(..., description="INTAKE, DRAFTING, DOL_PREVAILING_WAGE, USCIS_SUBMITTED, RFE_ISSUED, APPROVED, DENIED")
    uscis_receipt_number: Optional[str] = None


class RelocationDisbursementResult(BaseModel):
    case_id: str
    stipend_amount: float
    tax_gross_up_amount: float
    total_payable: float
    disbursement_reference: str
    message: str


class ImmigrationSummary(BaseModel):
    active_cases: int
    pending_uscis_receipts: int
    expiring_within_90_days_count: int
    total_relocation_outlay: float
