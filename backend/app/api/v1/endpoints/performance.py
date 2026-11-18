import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.core.rate_limit import check_ai_rate_limit
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.models.performance import PerformanceCycle, GoalOKR, ReviewFeedback
from backend.app.schemas.performance import (
    PerformanceCycleCreate,
    PerformanceCycleResponse,
    GoalOKRCreate,
    GoalOKRUpdate,
    GoalOKRResponse,
    ReviewFeedbackCreate,
    ReviewFeedbackResponse,
    ReviewAISynthesisRequest,
    ReviewAISynthesisResponse,
)
from backend.app.services.performance_service import performance_service

router = APIRouter()

@router.get("/cycles", response_model=List[PerformanceCycleResponse], summary="List performance review cycles")
async def list_cycles(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.list_cycles(db=db, org_id=current_user.organization_id)

@router.post("/cycles", response_model=PerformanceCycleResponse, status_code=status.HTTP_201_CREATED, summary="Create performance cycle")
async def create_cycle(
    data: PerformanceCycleCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.create_cycle(db=db, org_id=current_user.organization_id, data=data)

@router.post("/goals", response_model=GoalOKRResponse, status_code=status.HTTP_201_CREATED, summary="Create personal or team goal")
async def create_goal(
    data: GoalOKRCreate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.create_goal(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id,
        data=data
    )

@router.patch("/goals/{goal_id}", response_model=GoalOKRResponse, summary="Update goal progress percentage or status")
async def update_goal(
    goal_id: uuid.UUID,
    data: GoalOKRUpdate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.update_goal(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id,
        goal_id=goal_id,
        data=data
    )

@router.get("/goals/me", response_model=List[GoalOKRResponse], summary="Get own goals for a cycle")
async def get_my_goals(
    cycle_id: Optional[uuid.UUID] = Query(None),
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.list_goals(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id,
        cycle_id=cycle_id
    )

@router.post("/reviews", response_model=ReviewFeedbackResponse, status_code=status.HTTP_201_CREATED, summary="Submit 360 review feedback")
async def submit_review(
    data: ReviewFeedbackCreate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    feedback = await performance_service.submit_review(
        db=db,
        org_id=current_user.organization_id,
        reviewer_id=current_user.id,
        data=data
    )
    return ReviewFeedbackResponse.model_validate(feedback)

@router.post("/reviews/synthesize", response_model=ReviewAISynthesisResponse, summary="Synthesize 360 feedback with AI")
async def synthesize_review(
    req: ReviewAISynthesisRequest,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    _rate_limit: None = Depends(check_ai_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    return await performance_service.synthesize_360(
        db=db,
        org_id=current_user.organization_id,
        cycle_id=req.cycle_id,
        reviewee_id=req.reviewee_id
    )
