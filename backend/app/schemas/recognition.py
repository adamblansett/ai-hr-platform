from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PeerRecognitionCreate(BaseModel):
    sender_id: str
    recipient_id: str
    points: int = Field(50, ge=10, le=500)
    core_value: str = Field(..., description="CUSTOMER_OBSESSION, BIAS_FOR_ACTION, INNOVATION_EXCELLENCE, INCLUSION_AND_RESPECT, DELIVER_RESULTS, OWNERSHIP")
    message: str = Field(..., min_length=5)
    is_public: bool = True


class PeerRecognitionResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    points: int
    core_value: str
    message: str
    is_public: bool
    created_at: datetime


class RewardCatalogItemResponse(BaseModel):
    id: str
    title: str
    category: str
    points_cost: int
    description: str
    is_available: bool
    image_url: Optional[str] = None


class RewardRedemptionRequest(BaseModel):
    employee_id: str
    reward_item_id: str


class EmployeeWalletResponse(BaseModel):
    employee_id: str
    points_balance: int
    monthly_allowance_remaining: int
    updated_at: datetime


class MilestoneEvent(BaseModel):
    employee_id: str
    employee_name: str
    milestone_type: str
    milestone_date: str
    anniversary_years: Optional[int] = None
    suggested_award_points: int
