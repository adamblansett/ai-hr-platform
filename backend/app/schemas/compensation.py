import uuid
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.models.compensation import PayFrequency, EquityGrantType

class CompensationPackageCreate(BaseModel):
    employee_id: uuid.UUID
    base_salary: float = Field(..., gt=0)
    currency: str = Field("USD", max_length=10)
    effective_date: date
    pay_frequency: PayFrequency = PayFrequency.BI_WEEKLY
    target_bonus_percentage: float = 0.0

class CompensationPackageResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    base_salary: float
    currency: str
    effective_date: date
    pay_frequency: PayFrequency
    target_bonus_percentage: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class EquityGrantCreate(BaseModel):
    employee_id: uuid.UUID
    grant_number: str
    grant_type: EquityGrantType = EquityGrantType.RSU
    total_shares: int = Field(..., gt=0)
    strike_price: float = 0.0
    grant_date: date
    vesting_start_date: date
    cliff_months: int = 12
    vesting_duration_months: int = 48

class VestingScheduleMilestone(BaseModel):
    vest_date: date
    shares_vesting: int
    cumulative_vested_shares: int
    vesting_percentage: float
    is_cliff: bool

class EquityGrantResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    grant_number: str
    grant_type: EquityGrantType
    total_shares: int
    strike_price: float
    grant_date: date
    vesting_start_date: date
    cliff_months: int
    vesting_duration_months: int
    vested_shares_to_date: int
    unvested_shares: int
    schedule_preview: List[VestingScheduleMilestone] = Field(default_factory=list)

    class Config:
        from_attributes = True

class PaystubResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_amount: float
    net_amount: float
    tax_withholdings: Dict[str, float]
    benefit_deductions: Dict[str, float]
    pdf_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EmployeeTotalRewardsSummary(BaseModel):
    employee_id: uuid.UUID
    base_salary: float
    currency: str
    target_bonus_annual: float
    total_cash_compensation: float
    equity_grants_count: int
    total_granted_shares: int
    total_vested_shares: int
    equity_grants: List[EquityGrantResponse]
    recent_paystubs: List[PaystubResponse]
