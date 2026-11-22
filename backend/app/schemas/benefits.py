from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class BenefitPlanOut(BaseModel):
    id: str
    organization_id: str
    plan_name: str
    plan_type: str
    provider: str
    tier_name: str
    monthly_employee_premium: float
    monthly_employer_contribution: float
    annual_deductible: float
    out_of_pocket_max: float
    summary_of_benefits: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class BenefitElectionCreate(BaseModel):
    plan_id: str
    coverage_tier: str = "EMPLOYEE_ONLY" # EMPLOYEE_ONLY, EMPLOYEE_PLUS_SPOUSE, EMPLOYEE_PLUS_CHILDREN, FAMILY
    effective_date: date


class BenefitElectionOut(BaseModel):
    id: str
    employee_id: str
    plan_id: str
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None
    coverage_tier: str
    effective_date: date
    employee_monthly_cost: float
    employer_monthly_cost: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BenefitsAdvisorQuery(BaseModel):
    question: str
    family_members_count: Optional[int] = 1
    has_chronic_needs: Optional[bool] = False


class BenefitsAdvisorResponse(BaseModel):
    question: str
    recommended_plan_name: str
    recommendation_reason: str
    estimated_annual_employee_cost: float
    coverage_highlights: List[str]
