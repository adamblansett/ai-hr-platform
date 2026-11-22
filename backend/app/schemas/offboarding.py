from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class OffboardingInitiateRequest(BaseModel):
    employee_id: str
    last_working_day: date
    termination_reason: str = "VOLUNTARY_RESIGNATION"
    notes: Optional[str] = None


class OffboardingTaskOut(BaseModel):
    id: str
    title: str
    category: str
    assigned_to: str
    is_completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExitInterviewSubmit(BaseModel):
    primary_reason: str
    experience_rating: int = 4
    manager_feedback: Optional[str] = None
    company_culture_feedback: Optional[str] = None


class ExitInterviewOut(BaseModel):
    id: str
    primary_reason: str
    experience_rating: int
    manager_feedback: Optional[str]
    company_culture_feedback: Optional[str]
    ai_synthesized_insights: Dict[str, Any]
    submitted_at: datetime

    class Config:
        from_attributes = True


class OffboardingRecordOut(BaseModel):
    id: str
    organization_id: str
    employee_id: str
    employee_name: Optional[str] = None
    last_working_day: date
    termination_reason: str
    status: str
    scim_deprovisioned: bool
    equipment_returned: bool
    nda_reaffirmed: bool
    notes: Optional[str]
    tasks: List[OffboardingTaskOut] = []
    exit_interview: Optional[ExitInterviewOut] = None
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
