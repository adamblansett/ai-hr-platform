from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.schemas.analytics import (
    HROverviewMetrics,
    LeaveUtilizationAnalytics,
    PerformanceCalibrationMetrics,
)
from backend.app.services.analytics_service import analytics_service

router = APIRouter()

@router.get("/overview", response_model=HROverviewMetrics, summary="Organization-wide headcount and onboarding analytics")
async def get_hr_overview(
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_hr_overview(db, current_user.organization_id)

@router.get("/leave-utilization", response_model=LeaveUtilizationAnalytics, summary="Departmental leave utilization and balance metrics")
async def get_leave_analytics(
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_leave_utilization(db, current_user.organization_id)

@router.get("/performance-calibration", response_model=PerformanceCalibrationMetrics, summary="Performance calibration & OKR completion rates")
async def get_performance_calibration(
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_performance_calibration(db, current_user.organization_id)
