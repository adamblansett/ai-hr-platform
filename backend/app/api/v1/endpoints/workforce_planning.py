from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.schemas.workforce_planning import (
    RecruiterSyncResponse,
    RequisitionForecastCreate,
    RequisitionForecastResponse,
    ScenarioForecastRequest,
    ScenarioForecastResult,
    WorkforcePlanCreate,
    WorkforcePlanResponse,
    WorkforcePlanningSummary,
)
from backend.app.services.workforce_planning_service import workforce_planning_service

router = APIRouter()


@router.get("/plans", response_model=List[WorkforcePlanResponse])
def list_workforce_plans():
    """List departmental headcount plans and approved hiring budgets."""
    return workforce_planning_service.list_plans()


@router.post("/plans", response_model=WorkforcePlanResponse, status_code=status.HTTP_201_CREATED)
def create_workforce_plan(
    payload: WorkforcePlanCreate,
    current_user: Employee = Depends(
        require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])
    ),
):
    """Create a new departmental headcount & budget forecast plan."""
    return workforce_planning_service.create_plan(payload, organization_id=str(current_user.organization_id))


@router.post("/plans/{plan_id}/simulate", response_model=ScenarioForecastResult)
def simulate_workforce_scenario(plan_id: str, payload: ScenarioForecastRequest):
    """Run Conservative / Baseline / Hypergrowth headcount and fully-loaded cost simulation."""
    try:
        return workforce_planning_service.simulate_plan(plan_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/plans/{plan_id}/requisitions", response_model=RequisitionForecastResponse, status_code=status.HTTP_201_CREATED)
def create_requisition_forecast(plan_id: str, payload: RequisitionForecastCreate):
    """Add a planned headcount requisition under an active workforce plan."""
    try:
        return workforce_planning_service.add_requisition(plan_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/requisitions/{req_id}/sync-recruiter", response_model=RecruiterSyncResponse)
def sync_requisition_to_recruiter(req_id: str):
    """Sync an approved headcount requisition to ai-recruiter with an HMAC-SHA256 signed payload."""
    try:
        return workforce_planning_service.sync_requisition_to_recruiter(req_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/summary", response_model=WorkforcePlanningSummary)
def get_workforce_planning_summary():
    """Return executive summary of headcount targets, budgets, and ai-recruiter sync status."""
    return workforce_planning_service.get_summary()
