from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PulseSurveyCreate(BaseModel):
    title: str
    question: str
    category: Optional[str] = "ENGAGEMENT"


class PulseSurveyOut(BaseModel):
    id: str
    organization_id: str
    title: str
    question: str
    category: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PulseResponseSubmit(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None


class PulseResponseOut(BaseModel):
    id: str
    survey_id: str
    department: str
    rating: int
    feedback_text: Optional[str]
    sentiment_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentSentimentOut(BaseModel):
    department: str
    period: str
    enps_score: float
    avg_rating: float
    burnout_risk_level: str
    total_responses: int
    ai_action_recommendations: List[str]

    class Config:
        from_attributes = True


class PulseAnalyticsSummary(BaseModel):
    overall_enps: float
    overall_avg_rating: float
    total_responses: int
    departments: List[DepartmentSentimentOut]
    burnout_watchlists: List[str]
