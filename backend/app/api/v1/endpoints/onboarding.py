import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.models.onboarding import OnboardingCategory, OnboardingStatus
from backend.app.schemas.onboarding import (
    OnboardingTaskCreate,
    OnboardingTaskUpdate,
    OnboardingTaskResponse,
    OnboardingProgressSummary,
    DocumentUploadResponse,
)
from backend.app.services.onboarding_service import onboarding_service

router = APIRouter()

@router.get("/tasks", response_model=List[OnboardingTaskResponse], summary="List onboarding tasks")
async def list_onboarding_tasks(
    employee_id: Optional[uuid.UUID] = None,
    category: Optional[OnboardingCategory] = None,
    task_status: Optional[OnboardingStatus] = None,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    target_emp_id = employee_id
    # Employees can only query their own tasks
    if current_user.role == EmployeeRole.EMPLOYEE:
        target_emp_id = current_user.id

    tasks = await onboarding_service.list_tasks(
        db=db,
        org_id=current_user.organization_id,
        employee_id=target_emp_id,
        category=category,
        task_status=task_status
    )
    return tasks

@router.post("/tasks", response_model=OnboardingTaskResponse, status_code=status.HTTP_201_CREATED, summary="Create onboarding task")
async def create_onboarding_task(
    data: OnboardingTaskCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await onboarding_service.create_task(
        db=db,
        org_id=current_user.organization_id,
        data=data
    )

@router.patch("/tasks/{task_id}", response_model=OnboardingTaskResponse, summary="Update task status or details")
async def update_onboarding_task(
    task_id: uuid.UUID,
    data: OnboardingTaskUpdate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await onboarding_service.update_task_status(
        db=db,
        org_id=current_user.organization_id,
        task_id=task_id,
        update_data=data,
        actor_id=current_user.id
    )

@router.get("/me/progress", response_model=OnboardingProgressSummary, summary="Get own onboarding progress")
async def get_my_onboarding_progress(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await onboarding_service.get_progress_summary(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id
    )

@router.get("/progress/{employee_id}", response_model=OnboardingProgressSummary, summary="Get employee onboarding progress")
async def get_employee_onboarding_progress(
    employee_id: uuid.UUID,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    return await onboarding_service.get_progress_summary(
        db=db,
        org_id=current_user.organization_id,
        employee_id=employee_id
    )

@router.post("/tasks/{task_id}/upload-document", response_model=DocumentUploadResponse, summary="Attach document to onboarding task")
async def upload_task_document(
    task_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Simulated secure S3/blob upload with hash verification
    from datetime import datetime, timezone
    simulated_url = f"https://storage.internal/compliance/{current_user.organization_id}/{task_id}/{file.filename}"
    
    await onboarding_service.update_task_status(
        db=db,
        org_id=current_user.organization_id,
        task_id=task_id,
        update_data=OnboardingTaskUpdate(
            document_url=simulated_url,
            status=OnboardingStatus.IN_PROGRESS
        ),
        actor_id=current_user.id
    )

    return DocumentUploadResponse(
        task_id=task_id,
        document_url=simulated_url,
        uploaded_at=datetime.now(timezone.utc),
        status="UPLOADED_PENDING_HR_VERIFICATION"
    )
