from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.expenses import (
    ExpenseReportCreate,
    ExpenseReportResponse,
    ExpenseAuditResult,
)
from backend.app.services.expenses_service import expenses_service

router = APIRouter()


@router.post("/", response_model=ExpenseReportResponse, status_code=status.HTTP_201_CREATED)
def create_expense_report(payload: ExpenseReportCreate):
    """Create a new expense report with itemized expenses."""
    return expenses_service.create_report(payload)


@router.get("/", response_model=List[ExpenseReportResponse])
def list_expense_reports(employee_id: Optional[str] = Query(None)):
    """List all expense reports, optionally filtered by employee ID."""
    return expenses_service.list_reports(employee_id=employee_id)


@router.get("/{report_id}", response_model=ExpenseReportResponse)
def get_expense_report(report_id: str):
    """Retrieve an expense report by ID."""
    rep = expenses_service.get_report(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Expense report not found")
    return rep


@router.post("/{report_id}/audit", response_model=ExpenseAuditResult)
def audit_expense_report(report_id: str):
    """Run an automated policy compliance audit on an expense report."""
    try:
        return expenses_service.audit_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{report_id}/submit", response_model=ExpenseReportResponse)
def submit_expense_report(report_id: str):
    """Submit an expense report for manager approval and trigger compliance audit."""
    try:
        return expenses_service.submit_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{report_id}/approve", response_model=ExpenseReportResponse)
def approve_expense_report(report_id: str):
    """Approve an expense report and generate a reimbursement reference code."""
    try:
        return expenses_service.approve_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
