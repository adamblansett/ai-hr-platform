from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class SafetyIncidentCreate(BaseModel):
    employee_id: str
    incident_type: str = Field(..., description="INJURY, ILLNESS, NEAR_MISS, ENVIRONMENTAL, PROPERTY_DAMAGE")
    severity: str = Field(..., description="FIRST_AID, MEDICAL_TREATMENT, RESTRICTED_DUTY, DAYS_AWAY, FATALITY")
    incident_date: str = Field(..., description="YYYY-MM-DD")
    location: str
    description: str
    lost_workday_count: int = 0
    restricted_days_count: int = 0


class SafetyIncidentResponse(BaseModel):
    id: str
    employee_id: str
    incident_type: str
    severity: str
    incident_date: str
    location: str
    description: str
    is_osha_recordable: bool
    osha_case_number: Optional[str] = None
    lost_workday_count: int
    restricted_days_count: int
    ai_root_cause_analysis: Optional[str] = None
    corrective_actions: Optional[str] = None
    status: str
    created_at: datetime


class OSHA300LogSummary(BaseModel):
    year: int
    total_incidents: int
    osha_recordable_cases: int
    total_lost_workdays: int
    total_restricted_days: int
    injuries_count: int
    illnesses_count: int
    near_misses_count: int
    lost_workday_rate: float
