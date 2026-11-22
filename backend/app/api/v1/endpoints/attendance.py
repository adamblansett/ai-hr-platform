from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.attendance import TimeSheetEntry
from backend.app.schemas.attendance import (
    ClockInRequest,
    ClockOutRequest,
    TimeSheetEntryOut,
    AttendanceSummaryOut,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.attendance_service import AttendanceService

router = APIRouter()


@router.post("/clock-in", response_model=TimeSheetEntryOut, status_code=status.HTTP_201_CREATED)
async def clock_in(
    request: Request,
    req: ClockInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Clock in for a work shift."""
    client_ip = request.client.host if request.client else None
    try:
        return await AttendanceService.clock_in(
            db,
            org_id=current_user.organization_id,
            employee_id=current_user.id,
            ip_address=client_ip,
            notes=req.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clock-out", response_model=TimeSheetEntryOut)
async def clock_out(
    req: ClockOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Clock out and automatically audit statutory overtime and meal breaks."""
    try:
        return await AttendanceService.clock_out(
            db,
            employee_id=current_user.id,
            meal_break_minutes=req.meal_break_minutes,
            notes=req.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/timesheets/me", response_model=List[TimeSheetEntryOut])
async def list_my_timesheets(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """View logged timesheets and shift history."""
    res = await db.execute(
        select(TimeSheetEntry)
        .where(TimeSheetEntry.employee_id == current_user.id)
        .order_by(TimeSheetEntry.shift_date.desc())
        .limit(30)
    )
    return res.scalars().all()


@router.get("/summary/{employee_id}", response_model=AttendanceSummaryOut)
async def get_attendance_summary(
    employee_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Retrieve pay-period timesheet audit and payable hours calculation."""
    return await AttendanceService.get_summary(db, employee_id, start_date, end_date)
