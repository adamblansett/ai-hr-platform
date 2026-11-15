import enum
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Date, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class EmployeeRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    HR_ADMIN = "HR_ADMIN"
    PEOPLE_MANAGER = "PEOPLE_MANAGER"
    EMPLOYEE = "EMPLOYEE"

class EmploymentStatus(str, enum.Enum):
    ONBOARDING = "ONBOARDING"
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"

class EmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"
    INTERN = "INTERN"

class Employee(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "employees"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    role: Mapped[EmployeeRole] = mapped_column(
        Enum(EmployeeRole), default=EmployeeRole.EMPLOYEE, nullable=False
    )
    status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus), default=EmploymentStatus.ONBOARDING, index=True, nullable=False
    )
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType), default=EmploymentType.FULL_TIME, nullable=False
    )

    department: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Custom attributes & metadata (e.g. emergency contacts, custom fields)
    custom_attributes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", remote_side="Employee.id", backref="direct_reports"
    )
    onboarding_tasks: Mapped[List["OnboardingTask"]] = relationship(
        "OnboardingTask", back_populates="employee", cascade="all, delete-orphan", foreign_keys="OnboardingTask.employee_id"
    )
    leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        "LeaveRequest", back_populates="employee", cascade="all, delete-orphan", foreign_keys="LeaveRequest.employee_id"
    )
    policy_acknowledgments: Mapped[List["PolicyAcknowledgment"]] = relationship(
        "PolicyAcknowledgment", back_populates="employee", cascade="all, delete-orphan"
    )
