import uuid
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from backend.app.models.performance import CycleStatus, GoalStatus, ReviewRelationship

class PerformanceCycleCreate(BaseModel):
    title: str = Field(..., max_length=200)
    start_date: date
    end_date: date
    rubric_config: Dict[str, Any] = Field(default_factory=dict)

class PerformanceCycleResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    start_date: date
    end_date: date
    status: CycleStatus
    rubric_config: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class GoalOKRCreate(BaseModel):
    cycle_id: uuid.UUID
    title: str = Field(..., max_length=255)
    description: str
    key_results: Dict[str, Any] = Field(default_factory=dict)

class GoalOKRUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    key_results: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[GoalStatus] = None

class GoalOKRResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    cycle_id: uuid.UUID
    employee_id: uuid.UUID
    title: str
    description: str
    key_results: Dict[str, Any]
    progress_percentage: float
    status: GoalStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewFeedbackCreate(BaseModel):
    cycle_id: uuid.UUID
    reviewee_id: uuid.UUID
    relationship: ReviewRelationship
    ratings: Dict[str, Any] = Field(default_factory=dict) # e.g. {"execution": 4.5, "leadership": 4.0}
    qualitative_feedback: str = Field(..., min_length=10)

class ReviewFeedbackResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    cycle_id: uuid.UUID
    reviewee_id: uuid.UUID
    reviewee_name: Optional[str] = None
    reviewer_id: uuid.UUID
    reviewer_name: Optional[str] = None
    relationship: ReviewRelationship
    ratings: Dict[str, Any]
    qualitative_feedback: str
    ai_synthesized_summary: Optional[str] = None
    is_submitted: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewAISynthesisRequest(BaseModel):
    cycle_id: uuid.UUID
    reviewee_id: uuid.UUID

class ReviewAISynthesisResponse(BaseModel):
    cycle_id: uuid.UUID
    reviewee_id: uuid.UUID
    synthesized_summary: str
    key_strengths: List[str]
    growth_opportunities: List[str]
    overall_sentiment: str
    feedback_count: int
