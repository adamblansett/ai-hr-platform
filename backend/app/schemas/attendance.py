from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class ClockInRequest(BaseModel):
    notes: Optional[str] = None


class ClockOutRequest(BaseModel):
    meal_break_minutes: int = Field(default=30, ge=0, le=180)
    notes: Optional[str] = None


class TimeSheetEntryOut(BaseModel):
    id: str
    employee_id: str
    shift_date: date
    clock_in: datetime
    clock_out: Optional[datetime]
    total_hours: float
    regular_hours: float
    overtime_hours: float
    double_time_hours: float
    meal_break_minutes: int
    meal_penalty_flag: bool
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True


class AttendanceSummaryOut(BaseModel):
    employee_id: str
    period_start: date
    period_end: date
    total_shifts: int
    total_regular_hours: float
    total_overtime_hours: float
    total_double_time_hours: float
    meal_penalty_violations: int
    estimated_payable_hours: float
