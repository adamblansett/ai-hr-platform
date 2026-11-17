import uuid
from datetime import date, datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, EmailStr, Field
from backend.app.models.employee import EmploymentType

class RecruiterCandidate(BaseModel):
    recruiter_candidate_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: str
    department: str
    hire_date: date
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    manager_email: Optional[EmailStr] = None
    offer_signed_doc_url: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class RecruiterOfferAcceptedWebhook(BaseModel):
    event_id: str
    event_type: str = "candidate.offer_accepted"
    timestamp: datetime
    organization_id: uuid.UUID
    candidate: RecruiterCandidate

class RecruiterWebhookResponse(BaseModel):
    success: bool
    message: str
    employee_id: Optional[uuid.UUID] = None
    onboarding_tasks_created: int = 0
    external_idp_id: Optional[str] = None
