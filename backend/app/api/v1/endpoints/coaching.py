from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.coaching import OneOnOneMeeting, CalibrationSession
from backend.app.schemas.coaching import (
    OneOnOneAgendaGenerateRequest,
    OneOnOneOut,
    CalibrationAnalyzeRequest,
    CalibrationAnalysisOut,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.coaching_service import CoachingService

router = APIRouter()


@router.post("/1on1/generate-agenda", response_model=OneOnOneOut, status_code=status.HTTP_201_CREATED)
async def generate_one_on_one_agenda(
    req: OneOnOneAgendaGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Generate an AI-augmented 1:1 coaching agenda with talking points and prompts."""
    try:
        meeting = await CoachingService.generate_1on1_agenda(
            db, current_user.organization_id, current_user.id, req
        )
        return meeting
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/1on1/me", response_model=List[OneOnOneOut])
async def list_my_one_on_ones(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """List 1:1 check-in meetings for the current employee (either as manager or report)."""
    res = await db.execute(
        select(OneOnOneMeeting)
        .where(
            (OneOnOneMeeting.manager_id == current_user.id) |
            (OneOnOneMeeting.employee_id == current_user.id)
        )
        .order_by(OneOnOneMeeting.scheduled_date.desc())
    )
    return res.scalars().all()


@router.post("/calibration/analyze", response_model=CalibrationAnalysisOut)
async def analyze_performance_calibration(
    req: CalibrationAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Statistically analyze departmental review rating distribution to detect biases."""
    try:
        session = await CoachingService.analyze_calibration(db, current_user.organization_id, req)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/calibration/history", response_model=List[CalibrationAnalysisOut])
async def get_calibration_history(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """List historical calibration sessions and bias detection reports."""
    res = await db.execute(
        select(CalibrationSession)
        .where(CalibrationSession.organization_id == current_user.organization_id)
        .order_by(CalibrationSession.analyzed_at.desc())
    )
    sessions = res.scalars().all()
    for s in sessions:
        # compute mean for serialization
        total = s.total_reviewed or 1
        dist = s.rating_distribution or {}
        weighted_sum = sum(int(k) * int(v) for k, v in dist.items())
        s.mean_rating = round(weighted_sum / total, 2)
    return sessions
