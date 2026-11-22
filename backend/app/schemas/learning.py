from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    duration_minutes: int
    is_mandatory: bool
    passing_score_percentage: int
    certification_validity_days: int


class CourseEnrollmentResponse(BaseModel):
    id: str
    employee_id: str
    course_id: str
    course_title: Optional[str] = None
    status: str
    progress_percentage: int
    score: Optional[float] = None
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    certificate_id: Optional[str] = None


class CourseEnrollRequest(BaseModel):
    employee_id: str
    course_id: str


class CourseProgressUpdateRequest(BaseModel):
    progress_percentage: int = Field(..., ge=0, le=100)
    score: Optional[float] = Field(None, ge=0, le=100)


class ComplianceAuditSummary(BaseModel):
    total_mandatory_courses: int
    total_enrolled: int
    total_completed: int
    compliance_rate_percentage: float
    overdue_recertifications_count: int
    recommendations: List[str]
