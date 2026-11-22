from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.learning import (
    CourseResponse,
    CourseEnrollmentResponse,
    CourseEnrollRequest,
    CourseProgressUpdateRequest,
    ComplianceAuditSummary,
)
from backend.app.services.learning_service import learning_service

router = APIRouter()


@router.get("/courses", response_model=List[CourseResponse])
def list_courses(category: Optional[str] = Query(None)):
    """List available courses and compliance modules in the LMS."""
    return learning_service.list_courses(category=category)


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: str):
    """Retrieve details of a specific course."""
    course = learning_service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/enroll", response_model=CourseEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_course(payload: CourseEnrollRequest):
    """Enroll an employee in a course."""
    try:
        return learning_service.enroll_employee(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/enrollments/{enrollment_id}/progress", response_model=CourseEnrollmentResponse)
def update_enrollment_progress(enrollment_id: str, payload: CourseProgressUpdateRequest):
    """Update progress percentage and completion score."""
    try:
        return learning_service.update_progress(enrollment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/enrollments/me", response_model=List[CourseEnrollmentResponse])
def get_my_enrollments(employee_id: str = Query("emp-001")):
    """Get enrollments and certification status for the current user."""
    return learning_service.get_employee_enrollments(employee_id)


@router.get("/compliance-audit", response_model=ComplianceAuditSummary)
def get_compliance_audit():
    """Audit company-wide mandatory compliance training completion rates."""
    return learning_service.get_compliance_audit()
