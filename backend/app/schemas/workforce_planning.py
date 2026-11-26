from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkforcePlanCreate(BaseModel):
    fiscal_year: int = Field(2027, ge=2024, le=2035)
    department: str = Field(..., min_length=2, max_length=100)
    current_headcount: int = Field(..., ge=0)
    target_headcount: int = Field(..., ge=0)
    approved_budget_usd: float = Field(..., ge=0.0)
    projected_attrition_rate: float = Field(0.08, ge=0.0, le=1.0)


class RequisitionForecastCreate(BaseModel):
    role_title: str = Field(..., min_length=2, max_length=150)
    job_level: str = Field("L5", min_length=2, max_length=30)
    target_quarter: str = Field("Q1", min_length=2, max_length=10)
    estimated_base_salary: float = Field(..., gt=0.0)


class RequisitionForecastResponse(BaseModel):
    id: str
    plan_id: str
    organization_id: str
    role_title: str
    job_level: str
    target_quarter: str
    estimated_base_salary: float
    fully_loaded_cost: float
    recruiter_sync_status: str
    created_at: datetime


class WorkforcePlanResponse(BaseModel):
    id: str
    organization_id: str
    fiscal_year: int
    department: str
    current_headcount: int
    target_headcount: int
    approved_budget_usd: float
    projected_attrition_rate: float
    status: str
    ai_rationale: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requisitions: List[RequisitionForecastResponse] = Field(default_factory=list)


class ScenarioForecastRequest(BaseModel):
    scenario: str = Field("BASELINE", pattern="^(CONSERVATIVE|BASELINE|HYPERGROWTH)$")
    avg_base_salary: float = Field(165000.0, gt=0.0)


class ScenarioForecastResult(BaseModel):
    plan_id: str
    department: str
    scenario: str
    net_new_hires: int
    attrition_backfills: int
    total_hiring_need: int
    projected_headcount_end: int
    estimated_total_fully_loaded_cost: float
    budget_variance_usd: float
    ai_recommendation: str


class RecruiterSyncResponse(BaseModel):
    requisition_id: str
    recruiter_sync_status: str
    webhook_event: str
    signed_payload: Dict[str, Any]
    synced_at: datetime


class WorkforcePlanningSummary(BaseModel):
    total_plans: int
    total_current_headcount: int
    total_target_headcount: int
    total_approved_budget_usd: float
    total_open_requisitions: int
    synced_to_recruiter_count: int
