from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.pulse import PulseSurvey, PulseResponse
from backend.app.schemas.pulse import (
    PulseSurveyCreate,
    PulseSurveyOut,
    PulseResponseSubmit,
    PulseResponseOut,
    PulseAnalyticsSummary,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.pulse_service import PulseService

router = APIRouter()


@router.post("/surveys", response_model=PulseSurveyOut, status_code=status.HTTP_201_CREATED)
async def create_pulse_survey(
    survey_in: PulseSurveyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Publish a new micro-pulse survey across the organization."""
    survey = await PulseService.create_survey(db, current_user.organization_id, survey_in)
    return survey


@router.get("/active", response_model=List[PulseSurveyOut])
async def list_active_surveys(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """List active surveys available for employee feedback."""
    res = await db.execute(
        select(PulseSurvey).where(
            PulseSurvey.organization_id == current_user.organization_id,
            PulseSurvey.is_active == True
        )
    )
    return res.scalars().all()


@router.post("/surveys/{survey_id}/respond", response_model=PulseResponseOut)
async def submit_anonymous_pulse(
    survey_id: str,
    resp_in: PulseResponseSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Submit zero-knowledge anonymous feedback for a pulse survey."""
    try:
        response = await PulseService.submit_response(
            db,
            survey_id=survey_id,
            user_id=current_user.id,
            department=current_user.department or "General",
            data=resp_in,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics", response_model=PulseAnalyticsSummary)
async def get_pulse_sentiment_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Retrieve executive sentiment analytics, eNPS, and department burnout heatmaps."""
    return await PulseService.compute_pulse_analytics(db, current_user.organization_id)
