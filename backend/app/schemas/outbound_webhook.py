from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class WebhookSubscriptionCreate(BaseModel):
    target_url: str
    event_types: List[str]  # ["employee.hired", "leave.approved", "compensation.updated"]
    description: Optional[str] = None


class WebhookSubscriptionOut(BaseModel):
    id: str
    organization_id: str
    target_url: str
    event_types: List[str]
    is_active: bool
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryLogOut(BaseModel):
    id: str
    subscription_id: str
    event_type: str
    status_code: Optional[int]
    attempt_count: int
    delivered_at: datetime
    error_message: Optional[str]

    class Config:
        from_attributes = True


class WebhookTestPingResponse(BaseModel):
    status: str
    target_url: str
    signature_header: str
    test_event: str
    timestamp: str
