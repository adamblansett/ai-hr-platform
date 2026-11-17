import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.onboarding import OnboardingTask, OnboardingStatus, OnboardingCategory
from backend.app.models.employee import Employee, EmploymentStatus
from backend.app.models.audit import AuditLog
from backend.app.schemas.onboarding import (
    OnboardingTaskCreate,
    OnboardingTaskUpdate,
    OnboardingProgressSummary,
    OnboardingTaskResponse
)

class OnboardingService:
    @staticmethod
    async def create_task(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: OnboardingTaskCreate
    ) -> OnboardingTask:
        # Verify employee exists in organization
        emp_stmt = select(Employee).where(
            Employee.id == data.employee_id,
            Employee.organization_id == org_id
        )
        emp = (await db.execute(emp_stmt)).scalar_one_or_none()
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found in organization"
            )

        task = OnboardingTask(
            **data.model_dump(),
            organization_id=org_id,
            status=OnboardingStatus.PENDING
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: Optional[uuid.UUID] = None,
        category: Optional[OnboardingCategory] = None,
        task_status: Optional[OnboardingStatus] = None
    ) -> List[OnboardingTask]:
        query = select(OnboardingTask).where(OnboardingTask.organization_id == org_id)
        if employee_id:
            query = query.where(OnboardingTask.employee_id == employee_id)
        if category:
            query = query.where(OnboardingTask.category == category)
        if task_status:
            query = query.where(OnboardingTask.status == task_status)

        query = query.order_by(OnboardingTask.due_date.asc().nulls_last(), OnboardingTask.created_at.asc())
        return list((await db.execute(query)).scalars().all())

    @staticmethod
    async def update_task_status(
        db: AsyncSession,
        org_id: uuid.UUID,
        task_id: uuid.UUID,
        update_data: OnboardingTaskUpdate,
        actor_id: Optional[uuid.UUID] = None
    ) -> OnboardingTask:
        stmt = select(OnboardingTask).where(
            OnboardingTask.id == task_id,
            OnboardingTask.organization_id == org_id
        )
        task = (await db.execute(stmt)).scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding task not found"
            )

        data = update_data.model_dump(exclude_unset=True)
        if "status" in data and data["status"] == OnboardingStatus.COMPLETED and task.status != OnboardingStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)
        elif "status" in data and data["status"] != OnboardingStatus.COMPLETED:
            task.completed_at = None

        for k, v in data.items():
            setattr(task, k, v)

        # Audit log for compliance
        audit = AuditLog(
            organization_id=org_id,
            actor_id=actor_id,
            action="ONBOARDING_TASK_UPDATED",
            entity_type="OnboardingTask",
            entity_id=str(task.id),
            details={"task_title": task.title, "new_status": task.status.value},
            pii_redacted=True
        )
        db.add(audit)

        await db.commit()
        await db.refresh(task)

        # Check if all tasks for employee are completed, transition employee to ACTIVE if so
        await OnboardingService._check_and_activate_employee(db, org_id, task.employee_id)

        return task

    @staticmethod
    async def _check_and_activate_employee(db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID) -> None:
        stmt = select(OnboardingTask).where(
            OnboardingTask.employee_id == employee_id,
            OnboardingTask.organization_id == org_id
        )
        tasks = (await db.execute(stmt)).scalars().all()
        if not tasks:
            return

        all_completed = all(t.status in (OnboardingStatus.COMPLETED, OnboardingStatus.WAIVED) for t in tasks)
        if all_completed:
            emp_stmt = select(Employee).where(Employee.id == employee_id, Employee.organization_id == org_id)
            emp = (await db.execute(emp_stmt)).scalar_one_or_none()
            if emp and emp.status == EmploymentStatus.ONBOARDING:
                emp.status = EmploymentStatus.ACTIVE
                audit = AuditLog(
                    organization_id=org_id,
                    actor_id=None,
                    action="EMPLOYEE_STATUS_TRANSITIONED_TO_ACTIVE",
                    entity_type="Employee",
                    entity_id=str(emp.id),
                    details={"reason": "All onboarding tasks completed"},
                    pii_redacted=True
                )
                db.add(audit)
                await db.commit()

    @staticmethod
    async def get_progress_summary(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID
    ) -> OnboardingProgressSummary:
        tasks = await OnboardingService.list_tasks(db, org_id, employee_id=employee_id)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status in (OnboardingStatus.COMPLETED, OnboardingStatus.WAIVED))
        pending = sum(1 for t in tasks if t.status in (OnboardingStatus.PENDING, OnboardingStatus.IN_PROGRESS))
        blocked = sum(1 for t in tasks if t.status == OnboardingStatus.BLOCKED)
        pct = (completed / total * 100.0) if total > 0 else 0.0

        task_responses = [OnboardingTaskResponse.model_validate(t) for t in tasks]
        return OnboardingProgressSummary(
            total_tasks=total,
            completed_tasks=completed,
            pending_tasks=pending,
            blocked_tasks=blocked,
            completion_percentage=round(pct, 1),
            tasks=task_responses
        )

onboarding_service = OnboardingService()
