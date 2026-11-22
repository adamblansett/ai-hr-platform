from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.safety import (
    SafetyIncidentCreate,
    SafetyIncidentResponse,
    OSHA300LogSummary,
)
from backend.app.services.safety_service import safety_service

router = APIRouter()


@router.post("/incidents", response_model=SafetyIncidentResponse, status_code=status.HTTP_201_CREATED)
def report_safety_incident(payload: SafetyIncidentCreate):
    """File a new workplace incident and evaluate OSHA recordability."""
    return safety_service.report_incident(payload)


@router.get("/incidents", response_model=List[SafetyIncidentResponse])
def list_safety_incidents(employee_id: Optional[str] = Query(None)):
    """List workplace health, safety, and near-miss incidents."""
    return safety_service.list_incidents(employee_id=employee_id)


@router.get("/osha-300-log", response_model=OSHA300LogSummary)
def get_osha_300_log(year: int = Query(2026, description="Calendar year for OSHA 300 compliance log")):
    """Compute OSHA Form 300 / 300A incident and lost-time metrics."""
    return safety_service.get_osha_300_log(year=year)
