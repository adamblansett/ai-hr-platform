from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.offboarding import OffboardingRecord, OffboardingTask
from backend.app.schemas.offboarding import (
    OffboardingInitiateRequest,
    OffboardingRecordOut,
    OffboardingTaskOut,
    ExitInterviewSubmit,
    ExitInterviewOut,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.offboarding_service import OffboardingService

router = APIRouter()


@router.post("/initiate", response_model=OffboardingRecordOut, status_code=status.HTTP_201_CREATED)
async def initiate_employee_offboarding(
    req: OffboardingInitiateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Initiate structured offboarding workflow for an employee."""
    try:
        record = await OffboardingService.initiate_offboarding(
            db, current_user.organization_id, current_user.id, req
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=List[OffboardingRecordOut])
async def list_offboarding_records(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """List active and historical offboarding records."""
    res = await db.execute(
        select(OffboardingRecord)
        .where(OffboardingRecord.organization_id == current_user.organization_id)
        .order_by(OffboardingRecord.created_at.desc())
    )
    return res.scalars().all()


@router.post("/{offboarding_id}/deprovision-scim", response_model=OffboardingRecordOut)
async def deprovision_scim_accounts(
    offboarding_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Trigger automated SCIM 2.0 account suspension across IdPs."""
    try:
        record = await OffboardingService.trigger_scim_deprovisioning(
            db, offboarding_id, actor_id=current_user.id
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{offboarding_id}/exit-interview", response_model=ExitInterviewOut)
async def submit_exit_interview(
    offboarding_id: str,
    data: ExitInterviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """Submit exit interview feedback and trigger AI sentiment synthesis."""
    try:
        feedback = await OffboardingService.submit_exit_interview(db, offboarding_id, data)
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/tasks/{task_id}/toggle", response_model=OffboardingTaskOut)
async def toggle_offboarding_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER"])),
):
    """Toggle completion status of an offboarding task."""
    res = await db.execute(select(OffboardingTask).where(OffboardingTask.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = not task.is_completed
    await db.commit()
    await db.refresh(task)
    return task
