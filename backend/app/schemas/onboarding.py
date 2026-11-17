import uuid
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from backend.app.models.onboarding import OnboardingCategory, OnboardingStatus

class OnboardingTaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    category: OnboardingCategory = OnboardingCategory.DOCUMENTATION
    due_date: Optional[date] = None
    assigned_to_role: str = "EMPLOYEE"
    document_url: Optional[str] = None
    external_system_payload: Dict[str, Any] = Field(default_factory=dict)

class OnboardingTaskCreate(OnboardingTaskBase):
    employee_id: uuid.UUID
    recruiter_candidate_id: Optional[str] = None
    offer_acceptance_reference: Optional[str] = None

class OnboardingTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[OnboardingCategory] = None
    status: Optional[OnboardingStatus] = None
    due_date: Optional[date] = None
    assigned_to_role: Optional[str] = None
    document_url: Optional[str] = None
    external_system_payload: Optional[Dict[str, Any]] = None

class OnboardingTaskResponse(OnboardingTaskBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    recruiter_candidate_id: Optional[str] = None
    offer_acceptance_reference: Optional[str] = None
    status: OnboardingStatus
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OnboardingProgressSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    blocked_tasks: int
    completion_percentage: float
    tasks: List[OnboardingTaskResponse]

class DocumentUploadResponse(BaseModel):
    task_id: uuid.UUID
    document_url: str
    uploaded_at: datetime
    status: str
