from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class SalaryBenchmarkCreate(BaseModel):
    job_title: str
    department: str
    job_level: str = "L5"
    geo_zone: str = "US_BAY_AREA"
    base_salary_p25: float = Field(..., gt=0)
    base_salary_p50: float = Field(..., gt=0)
    base_salary_p75: float = Field(..., gt=0)
    base_salary_p90: float = Field(..., gt=0)
    equity_shares_p50: float = 15000.0
    variable_bonus_target_pct: float = 15.0
    currency: str = "USD"


class SalaryBenchmarkResponse(BaseModel):
    id: str
    job_title: str
    department: str
    job_level: str
    geo_zone: str
    base_salary_p25: float
    base_salary_p50: float
    base_salary_p75: float
    base_salary_p90: float
    equity_shares_p50: float
    variable_bonus_target_pct: float
    currency: str
    updated_at: datetime


class EmployeeCompensationAudit(BaseModel):
    employee_id: str
    employee_name: str
    job_title: str
    department: str
    job_level: str
    geo_zone: str
    current_base_salary: float
    market_p50: float
    compa_ratio: float  # current / market_p50 (e.g. 1.05 = 5% above median)
    band_position: str  # BELOW_RANGE, LOWER_QUARTILE, AT_MARKET, UPPER_QUARTILE, ABOVE_RANGE
    suggested_merit_adjustment: float
    retention_risk_level: str  # LOW, MODERATE, HIGH


class DepartmentBenchmarkingSummary(BaseModel):
    department: str
    average_compa_ratio: float
    employees_below_p50_count: int
    total_budget_gap_to_p50: float
    audits: List[EmployeeCompensationAudit]
