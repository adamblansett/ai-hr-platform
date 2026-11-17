from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field
from backend.app.models.employee import EmployeeRole, EmploymentStatus, EmploymentType

class EmployeeBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    preferred_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)
    role: EmployeeRole = EmployeeRole.EMPLOYEE
    status: EmploymentStatus = EmploymentStatus.ONBOARDING
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    department: str = Field(..., max_length=100)
    job_title: str = Field(..., max_length=150)
    manager_id: Optional[uuid.UUID] = None
    hire_date: date
    termination_date: Optional[date] = None
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)

class EmployeeCreate(EmployeeBase):
    password: Optional[str] = "TemporaryPass!2026"

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[EmployeeRole] = None
    status: Optional[EmploymentStatus] = None
    employment_type: Optional[EmploymentType] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None
    termination_date: Optional[date] = None
    custom_attributes: Optional[Dict[str, Any]] = None

class EmployeeSelfUpdate(BaseModel):
    preferred_name: Optional[str] = None
    phone_number: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None

class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmployeeDirectoryItem(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    preferred_name: Optional[str] = None
    email: str
    department: str
    job_title: str
    role: EmployeeRole
    status: EmploymentStatus
    manager_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

class PaginatedEmployeesResponse(BaseModel):
    items: List[EmployeeDirectoryItem]
    total: int
    page: int
    size: int
    total_pages: int

class OrgChartNode(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    job_title: str
    department: str
    manager_id: Optional[uuid.UUID] = None
    direct_reports: List[OrgChartNode] = Field(default_factory=list)

OrgChartNode.model_rebuild()
