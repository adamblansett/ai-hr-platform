import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from backend.app.schemas.learning import (
    CourseResponse,
    CourseEnrollmentResponse,
    CourseEnrollRequest,
    CourseProgressUpdateRequest,
    ComplianceAuditSummary,
)


class LearningService:
    def __init__(self):
        self._courses: Dict[str, dict] = {}
        self._enrollments: Dict[str, dict] = {}
        self._seed_default_courses()

    def _seed_default_courses(self):
        c1 = {
            "id": "course-sec-101",
            "title": "2026 Annual SOC 2 & Information Security Awareness",
            "description": "Mandatory corporate data protection, phishing defenses, zero trust access, and credential hygiene.",
            "category": "COMPLIANCE",
            "duration_minutes": 45,
            "is_mandatory": True,
            "passing_score_percentage": 85,
            "certification_validity_days": 365,
        }
        c2 = {
            "id": "course-harass-102",
            "title": "Preventing Workplace Harassment & Building Inclusive Teams",
            "description": "Statutory California & New York compliant respectful workplace and bystander intervention training.",
            "category": "COMPLIANCE",
            "duration_minutes": 60,
            "is_mandatory": True,
            "passing_score_percentage": 80,
            "certification_validity_days": 730,
        }
        c3 = {
            "id": "course-hipaa-103",
            "title": "HIPAA Privacy, Security & Protected Health Information (PHI)",
            "description": "Standards for handling sensitive employee health records and benefits enrollment data.",
            "category": "COMPLIANCE",
            "duration_minutes": 30,
            "is_mandatory": False,
            "passing_score_percentage": 80,
            "certification_validity_days": 365,
        }
        c4 = {
            "id": "course-arch-201",
            "title": "Cloud Native Architecture & Distributed Systems with Go/Python",
            "description": "Advanced engineering practices for decoupled microservices, event streaming, and resilient state machines.",
            "category": "TECHNICAL",
            "duration_minutes": 120,
            "is_mandatory": False,
            "passing_score_percentage": 75,
            "certification_validity_days": 1000,
        }
        for c in (c1, c2, c3, c4):
            self._courses[c["id"]] = c

        # Seed initial enrollments for emp-001
        e1 = {
            "id": "enr-001",
            "employee_id": "emp-001",
            "course_id": "course-sec-101",
            "status": "COMPLETED",
            "progress_percentage": 100,
            "score": 95.0,
            "enrolled_at": datetime(2026, 1, 15, 9, 0, 0),
            "completed_at": datetime(2026, 1, 15, 9, 48, 0),
            "expires_at": datetime(2027, 1, 15, 9, 48, 0),
            "certificate_id": "CERT-2026-SEC-891A",
        }
        e2 = {
            "id": "enr-002",
            "employee_id": "emp-001",
            "course_id": "course-harass-102",
            "status": "IN_PROGRESS",
            "progress_percentage": 65,
            "score": None,
            "enrolled_at": datetime(2026, 10, 1, 14, 0, 0),
            "completed_at": None,
            "expires_at": None,
            "certificate_id": None,
        }
        self._enrollments[e1["id"]] = e1
        self._enrollments[e2["id"]] = e2

    def list_courses(self, category: Optional[str] = None) -> List[CourseResponse]:
        courses = list(self._courses.values())
        if category:
            courses = [c for c in courses if c["category"] == category]
        return [CourseResponse(**c) for c in courses]

    def get_course(self, course_id: str) -> Optional[CourseResponse]:
        c = self._courses.get(course_id)
        return CourseResponse(**c) if c else None

    def enroll_employee(self, payload: CourseEnrollRequest) -> CourseEnrollmentResponse:
        course = self._courses.get(payload.course_id)
        if not course:
            raise ValueError(f"Course {payload.course_id} not found")

        # Check existing enrollment
        existing = next(
            (e for e in self._enrollments.values() if e["employee_id"] == payload.employee_id and e["course_id"] == payload.course_id),
            None,
        )
        if existing:
            existing["course_title"] = course["title"]
            return CourseEnrollmentResponse(**existing)

        enr_id = f"enr-{uuid.uuid4().hex[:8]}"
        record = {
            "id": enr_id,
            "employee_id": payload.employee_id,
            "course_id": payload.course_id,
            "status": "ENROLLED",
            "progress_percentage": 0,
            "score": None,
            "enrolled_at": datetime.utcnow(),
            "completed_at": None,
            "expires_at": None,
            "certificate_id": None,
        }
        self._enrollments[enr_id] = record
        record_copy = dict(record)
        record_copy["course_title"] = course["title"]
        return CourseEnrollmentResponse(**record_copy)

    def update_progress(self, enrollment_id: str, payload: CourseProgressUpdateRequest) -> CourseEnrollmentResponse:
        enr = self._enrollments.get(enrollment_id)
        if not enr:
            raise ValueError(f"Enrollment {enrollment_id} not found")

        course = self._courses.get(enr["course_id"])
        enr["progress_percentage"] = payload.progress_percentage

        if payload.score is not None:
            enr["score"] = payload.score

        if payload.progress_percentage >= 100:
            passing = (course["passing_score_percentage"] if course else 80)
            score = enr["score"] or 100.0
            if score >= passing:
                enr["status"] = "COMPLETED"
                enr["completed_at"] = datetime.utcnow()
                valid_days = course["certification_validity_days"] if course else 365
                enr["expires_at"] = datetime.utcnow() + timedelta(days=valid_days)
                enr["certificate_id"] = f"CERT-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"
            else:
                enr["status"] = "IN_PROGRESS"
        elif payload.progress_percentage > 0:
            enr["status"] = "IN_PROGRESS"

        res = dict(enr)
        res["course_title"] = course["title"] if course else None
        return CourseEnrollmentResponse(**res)

    def get_employee_enrollments(self, employee_id: str) -> List[CourseEnrollmentResponse]:
        results = []
        for enr in self._enrollments.values():
            if enr["employee_id"] == employee_id:
                c = self._courses.get(enr["course_id"])
                rec = dict(enr)
                rec["course_title"] = c["title"] if c else None
                results.append(CourseEnrollmentResponse(**rec))
        return results

    def get_compliance_audit(self) -> ComplianceAuditSummary:
        mandatory_courses = [c for c in self._courses.values() if c["is_mandatory"]]
        mandatory_ids = {c["id"] for c in mandatory_courses}

        mandatory_enrollments = [e for e in self._enrollments.values() if e["course_id"] in mandatory_ids]
        completed = [e for e in mandatory_enrollments if e["status"] == "COMPLETED"]

        total_enrolled = len(mandatory_enrollments)
        total_completed = len(completed)
        rate = round((total_completed / total_enrolled) * 100, 1) if total_enrolled > 0 else 100.0

        recommendations = [
            "Trigger automated Slack/Teams reminder for in-progress Anti-Harassment modules.",
            "Schedule upcoming SOC 2 recertification batch for Q1 2027.",
        ]

        return ComplianceAuditSummary(
            total_mandatory_courses=len(mandatory_courses),
            total_enrolled=total_enrolled,
            total_completed=total_completed,
            compliance_rate_percentage=rate,
            overdue_recertifications_count=0,
            recommendations=recommendations,
        )


learning_service = LearningService()
