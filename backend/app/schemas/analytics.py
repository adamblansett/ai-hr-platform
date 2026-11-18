import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class HROverviewMetrics(BaseModel):
    total_headcount: int
    active_employees: int
    onboarding_employees: int
    departments_count: int
    onboarding_completion_rate: float
    department_distribution: Dict[str, int]

class LeaveUtilizationAnalytics(BaseModel):
    total_leave_days_taken: float
    days_by_policy: Dict[str, float]
    department_utilization: Dict[str, float]
    pending_approval_count: int

class PerformanceCalibrationMetrics(BaseModel):
    cycle_id: Optional[uuid.UUID] = None
    cycle_title: Optional[str] = None
    total_reviews_submitted: int
    goal_completion_rate: float
    sentiment_breakdown: Dict[str, int]
    department_goal_progress: Dict[str, float]
