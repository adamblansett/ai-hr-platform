from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ExpenseItemCreate(BaseModel):
    category: str = Field(..., description="MEALS, TRAVEL, LODGING, SOFTWARE, OFFICE_SUPPLIES, OTHER")
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    expense_date: str = Field(..., description="YYYY-MM-DD")
    merchant: str
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class ExpenseItemResponse(BaseModel):
    id: str
    report_id: str
    category: str
    amount: float
    currency: str
    expense_date: str
    merchant: str
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    is_compliant: bool
    policy_flags: Optional[str] = None


class ExpenseReportCreate(BaseModel):
    employee_id: str
    title: str
    items: List[ExpenseItemCreate] = []


class ExpenseReportResponse(BaseModel):
    id: str
    employee_id: str
    title: str
    status: str
    total_amount: float
    currency: str
    audit_status: str
    audit_notes: Optional[str] = None
    reimbursement_reference: Optional[str] = None
    created_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    items: List[ExpenseItemResponse] = []


class ExpenseAuditRequest(BaseModel):
    report_id: str


class ExpenseAuditResult(BaseModel):
    report_id: str
    overall_status: str  # COMPLIANT, FLAGGED, REJECTED
    total_audited: float
    flagged_items_count: int
    flags: List[str]
    remediation_actions: List[str]
