from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ContractorCreate(BaseModel):
    full_name: str
    email: str
    country: str
    entity_type: str = "INDIVIDUAL"
    tax_form_type: str = "W8_BEN"
    hourly_rate: float = Field(75.0, gt=0)
    currency: str = "USD"


class ContractorResponse(BaseModel):
    id: str
    full_name: str
    email: str
    country: str
    entity_type: str
    tax_form_type: str
    tax_form_verified: bool
    tax_id_masked: Optional[str] = None
    hourly_rate: float
    currency: str
    status: str
    created_at: datetime


class SOWCreate(BaseModel):
    contractor_id: str
    title: str
    total_budget: float = Field(..., gt=0)
    currency: str = "USD"
    start_date: str
    end_date: str
    deliverables_description: Optional[str] = None


class SOWResponse(BaseModel):
    id: str
    contractor_id: str
    title: str
    total_budget: float
    currency: str
    start_date: str
    end_date: str
    status: str
    deliverables_description: Optional[str] = None


class InvoiceCreate(BaseModel):
    sow_id: str
    contractor_id: str
    milestone_title: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"


class InvoiceResponse(BaseModel):
    id: str
    sow_id: str
    contractor_id: str
    milestone_title: str
    amount: float
    currency: str
    status: str
    submitted_at: datetime
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    payout_tx_hash: Optional[str] = None


class EORSummary(BaseModel):
    active_contractors: int
    pending_tax_verifications: int
    total_active_sows: int
    total_invoiced_this_month: float
    total_paid_this_month: float
