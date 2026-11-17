import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.models.leave import LeaveType, LeaveStatus

class LeavePolicyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    leave_type: LeaveType
    annual_days_allowed: float = 15.0
    accrual_rate_per_month: float = 1.25
    max_carryover_days: float = 5.0
    requires_approval: bool = True

class LeavePolicyResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    leave_type: LeaveType
    annual_days_allowed: float
    accrual_rate_per_month: float
    max_carryover_days: float
    requires_approval: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LeaveBalanceResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    policy_id: uuid.UUID
    policy_name: str
    leave_type: LeaveType
    year: int
    accrued_days: float
    used_days: float
    carried_over_days: float
    remaining_days: float

class LeaveRequestCreate(BaseModel):
    policy_id: uuid.UUID
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=3, max_length=500)

class LeaveRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    employee_name: Optional[str] = None
    policy_id: uuid.UUID
    policy_name: Optional[str] = None
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: LeaveStatus
    approver_id: Optional[uuid.UUID] = None
    decision_reason: Optional[str] = None
    calendar_conflict_flag: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LeaveDecisionRequest(BaseModel):
    status: LeaveStatus # APPROVED or REJECTED
    decision_reason: Optional[str] = None
