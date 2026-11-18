from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SkillCreate(BaseModel):
    skill_name: str
    category: Optional[str] = "TECHNICAL"
    proficiency_level: int = Field(default=3, ge=1, le=5)
    verified_by_manager: Optional[bool] = False


class SkillOut(BaseModel):
    id: str
    employee_id: str
    skill_name: str
    category: str
    proficiency_level: int
    verified_by_manager: bool
    last_assessed_at: datetime

    class Config:
        from_attributes = True


class FlightRiskOut(BaseModel):
    id: str
    employee_id: str
    risk_score: float
    risk_level: str
    contributing_factors: List[str]
    recommended_interventions: List[str]
    evaluated_at: datetime

    class Config:
        from_attributes = True


class CandidateMatch(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    current_title: str
    match_score_percent: float
    matching_skills: List[str]
    missing_skills: List[str]


class RequisitionCreate(BaseModel):
    title: str
    department: str
    min_experience_years: int = 2
    required_skills: List[str]
    target_headcount: int = 1


class RequisitionOut(BaseModel):
    id: str
    organization_id: str
    title: str
    department: str
    min_experience_years: int
    required_skills: List[str]
    target_headcount: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
