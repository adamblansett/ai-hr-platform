from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.benefits import BenefitPlan, EmployeeBenefitElection
from backend.app.schemas.benefits import (
    BenefitPlanOut,
    BenefitElectionCreate,
    BenefitElectionOut,
    BenefitsAdvisorQuery,
    BenefitsAdvisorResponse,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.benefits_service import BenefitsService

router = APIRouter()


@router.get("/plans", response_model=List[BenefitPlanOut])
async def list_available_plans(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """List available healthcare, dental, vision, and retirement plans."""
    return await BenefitsService.get_or_seed_plans(db, current_user.organization_id)


@router.get("/elections/me", response_model=List[BenefitElectionOut])
async def get_my_elections(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """View current benefit elections and monthly payroll deductions."""
    res = await db.execute(
        select(EmployeeBenefitElection)
        .where(
            EmployeeBenefitElection.employee_id == current_user.id,
            EmployeeBenefitElection.status == "ACTIVE"
        )
    )
    elections = res.scalars().all()
    out = []
    for el in elections:
        p_res = await db.execute(select(BenefitPlan).where(BenefitPlan.id == el.plan_id))
        plan = p_res.scalar_one_or_none()
        item = BenefitElectionOut.model_validate(el)
        if plan:
            item.plan_name = plan.plan_name
            item.plan_type = plan.plan_type
        out.append(item)
    return out


@router.post("/elections", response_model=BenefitElectionOut, status_code=status.HTTP_201_CREATED)
async def enroll_in_plan(
    election_in: BenefitElectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Enroll in a benefit plan for the current plan year or qualifying life event."""
    try:
        election = await BenefitsService.enroll_employee(
            db, current_user.organization_id, current_user.id, election_in
        )
        return election
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/advisor/query", response_model=BenefitsAdvisorResponse)
async def ask_benefits_advisor(
    query: BenefitsAdvisorQuery,
    current_user: Employee = Depends(get_current_user),
):
    """Consult the AI Benefits Advisor for personalized plan recommendations."""
    return BenefitsService.advise_on_benefits(query)
