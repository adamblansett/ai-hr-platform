from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    recipient_employee_id: Optional[str] = "emp-001"
    channel: str = Field("IN_APP", pattern="^(EMAIL|SLACK|TEAMS|IN_APP)$")
    category: str = Field(
        "SECURITY_ALERT",
        pattern="^(LEAVE_APPROVAL|VISA_EXPIRY|COMPLIANCE_LMS|REVIEW_DEADLINE|ONBOARDING_REMINDER|SECURITY_ALERT)$",
    )
    title: str = Field(..., min_length=2, max_length=255)
    body: str = Field(..., min_length=2)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    id: str
    organization_id: str
    recipient_employee_id: Optional[str] = None
    channel: str
    category: str
    title: str
    body: str
    status: str
    metadata_json: Dict[str, Any]
    sent_at: Optional[datetime] = None
    created_at: datetime


class UnreadCountResponse(BaseModel):
    recipient_employee_id: str
    unread_count: int


class DigestSummaryResponse(BaseModel):
    organization_id: str
    generated_at: datetime
    expiring_visas_count: int
    pending_leave_approvals_count: int
    overdue_compliance_courses_count: int
    upcoming_review_deadlines_count: int
    dispatched_channels: List[str]
    digest_preview: str
