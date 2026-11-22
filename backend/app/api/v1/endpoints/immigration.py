from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.immigration import (
    ImmigrationCaseCreate,
    ImmigrationCaseResponse,
    CaseStatusUpdateRequest,
    RelocationDisbursementResult,
    ImmigrationSummary,
)
from backend.app.services.immigration_service import immigration_service

router = APIRouter()


@router.get("/cases", response_model=List[ImmigrationCaseResponse])
def list_immigration_cases(employee_id: Optional[str] = Query(None)):
    """List active and historical visa petitions and immigration cases."""
    return immigration_service.list_cases(employee_id=employee_id)


@router.post("/cases", response_model=ImmigrationCaseResponse, status_code=status.HTTP_201_CREATED)
def create_immigration_case(payload: ImmigrationCaseCreate):
    """File a new visa petition or legal permanent residency case."""
    return immigration_service.create_case(payload)


@router.patch("/cases/{case_id}/status", response_model=ImmigrationCaseResponse)
def update_case_status(case_id: str, payload: CaseStatusUpdateRequest):
    """Update case status milestone (e.g. DOL prevailing wage, USCIS submitted, approved)."""
    try:
        return immigration_service.update_case_status(case_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cases/{case_id}/disburse-stipend", response_model=RelocationDisbursementResult)
def disburse_relocation_stipend(case_id: str):
    """Calculate tax gross-up and disburse global relocation stipend via payroll."""
    try:
        return immigration_service.disburse_relocation_stipend(case_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/summary", response_model=ImmigrationSummary)
def get_immigration_summary():
    """Retrieve high-level immigration case pipeline metrics and relocation outlays."""
    return immigration_service.get_immigration_summary()
