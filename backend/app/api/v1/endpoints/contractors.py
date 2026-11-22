from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.contractors import (
    ContractorCreate,
    ContractorResponse,
    SOWCreate,
    SOWResponse,
    InvoiceCreate,
    InvoiceResponse,
    EORSummary,
)
from backend.app.services.contractors_service import contractors_service

router = APIRouter()


@router.get("/", response_model=List[ContractorResponse])
def list_contractors(country: Optional[str] = Query(None)):
    """List international contractors in the global EOR hub."""
    return contractors_service.list_contractors(country=country)


@router.post("/", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
def create_contractor(payload: ContractorCreate):
    """Onboard a new international contractor profile."""
    return contractors_service.create_contractor(payload)


@router.post("/{contractor_id}/verify-tax", response_model=ContractorResponse)
def verify_tax_form(contractor_id: str):
    """Mark contractor W-8BEN / W-9 / VAT documentation as audited and verified."""
    try:
        return contractors_service.verify_tax_form(contractor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sows", response_model=List[SOWResponse])
def list_sows(contractor_id: Optional[str] = Query(None)):
    """List Statements of Work (SOWs) and contractor engagements."""
    return contractors_service.list_sows(contractor_id=contractor_id)


@router.post("/sows", response_model=SOWResponse, status_code=status.HTTP_201_CREATED)
def create_sow(payload: SOWCreate):
    """Create a new Statement of Work (SOW) agreement."""
    return contractors_service.create_sow(payload)


@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(contractor_id: Optional[str] = Query(None)):
    """List contractor milestone invoices and payment statuses."""
    return contractors_service.list_invoices(contractor_id=contractor_id)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def submit_invoice(payload: InvoiceCreate):
    """Submit a milestone invoice against an active SOW."""
    try:
        return contractors_service.submit_invoice(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}/approve", response_model=InvoiceResponse)
def approve_invoice(invoice_id: str):
    """Approve a contractor milestone invoice for payout."""
    try:
        return contractors_service.approve_invoice(invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(invoice_id: str):
    """Execute cross-border invoice payout and generate transfer hash."""
    try:
        return contractors_service.pay_invoice(invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/summary/eor", response_model=EORSummary)
def get_eor_summary():
    """Retrieve global contractor headcount, compliance, and monthly outlay metrics."""
    return contractors_service.get_eor_summary()
