import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class CourseCategory(str, Enum):
    COMPLIANCE = "COMPLIANCE"
    TECHNICAL = "TECHNICAL"
    LEADERSHIP = "LEADERSHIP"
    ONBOARDING = "ONBOARDING"
    SAFETY = "SAFETY"


class EnrollmentStatus(str, Enum):
    ENROLLED = "ENROLLED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class Course(Base):
    __tablename__ = "learning_courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default=CourseCategory.COMPLIANCE.value)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    passing_score_percentage: Mapped[int] = mapped_column(Integer, default=80)
    certification_validity_days: Mapped[int] = mapped_column(Integer, default=365)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_courses.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=EnrollmentStatus.ENROLLED.value)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    certificate_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
