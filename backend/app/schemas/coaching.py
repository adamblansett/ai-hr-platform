from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class OneOnOneAgendaGenerateRequest(BaseModel):
    employee_id: str
    scheduled_date: date
    focus_area: Optional[str] = "GENERAL_PROGRESS" # GENERAL_PROGRESS, OKR_REVIEW, CAREER_GROWTH, PERFORMANCE_INTERVENTION


class OneOnOneOut(BaseModel):
    id: str
    organization_id: str
    manager_id: str
    employee_id: str
    scheduled_date: date
    status: str
    talking_points: List[str]
    ai_suggested_prompts: List[str]
    manager_notes: Optional[str] = None
    action_items: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class CalibrationAnalyzeRequest(BaseModel):
    cycle_name: str
    department: str
    ratings: List[int] = Field(..., description="List of ratings from 1 to 5")


class CalibrationAnalysisOut(BaseModel):
    id: str
    cycle_name: str
    department: str
    total_reviewed: int
    rating_distribution: Dict[str, int]
    mean_rating: float
    detected_biases: List[str]
    recommendations: List[str]
    analyzed_at: datetime

    class Config:
        from_attributes = True
