from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.succession import SkillCompetency, FlightRiskAssessment, InternalRequisition
from backend.app.schemas.succession import (
    SkillCreate, SkillOut, FlightRiskOut, CandidateMatch, RequisitionCreate, RequisitionOut
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.succession_service import SuccessionService

router = APIRouter()


@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
async def add_or_update_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Add or update an employee skill competency."""
    existing_res = await db.execute(
        select(SkillCompetency).where(
            SkillCompetency.employee_id == current_user.id,
            SkillCompetency.skill_name == skill_in.skill_name
        )
    )
    skill = existing_res.scalar_one_or_none()
    if skill:
        skill.proficiency_level = skill_in.proficiency_level
        skill.category = skill_in.category or skill.category
    else:
        skill = SkillCompetency(
            organization_id=current_user.organization_id,
            employee_id=current_user.id,
            skill_name=skill_in.skill_name,
            category=skill_in.category or "TECHNICAL",
            proficiency_level=skill_in.proficiency_level,
            verified_by_manager=False,
        )
        db.add(skill)

    await db.commit()
    await db.refresh(skill)
    return skill


@router.get("/skills/me", response_model=List[SkillOut])
async def get_my_skills(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """List skills for the logged-in employee."""
    res = await db.execute(select(SkillCompetency).where(SkillCompetency.employee_id == current_user.id))
    return res.scalars().all()


@router.post("/flight-risk/evaluate/{employee_id}", response_model=FlightRiskOut)
async def evaluate_flight_risk(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Assess and calculate flight risk for an employee."""
    try:
        assessment = await SuccessionService.assess_flight_risk(db, employee_id, current_user.organization_id)
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/flight-risk", response_model=List[FlightRiskOut])
async def list_flight_risks(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """List recorded flight risk assessments across the organization."""
    res = await db.execute(
        select(FlightRiskAssessment).where(FlightRiskAssessment.organization_id == current_user.organization_id)
    )
    return res.scalars().all()


@router.post("/requisitions", response_model=RequisitionOut, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    req_in: RequisitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Create an internal job requisition for internal mobility matching."""
    req = InternalRequisition(
        organization_id=current_user.organization_id,
        title=req_in.title,
        department=req_in.department,
        min_experience_years=req_in.min_experience_years,
        required_skills=req_in.required_skills,
        target_headcount=req_in.target_headcount,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


@router.get("/requisitions", response_model=List[RequisitionOut])
async def list_requisitions(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """List open internal requisitions."""
    res = await db.execute(
        select(InternalRequisition).where(InternalRequisition.organization_id == current_user.organization_id)
    )
    return res.scalars().all()


@router.get("/requisitions/{req_id}/match", response_model=List[CandidateMatch])
async def match_internal_candidates(
    req_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Match internal employees to an internal requisition based on skill taxonomy."""
    try:
        matches = await SuccessionService.match_candidates(db, req_id, current_user.organization_id)
        return matches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
