import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.models.leave import LeavePolicy, LeaveRequest, LeaveStatus
from backend.app.schemas.leave import (
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveDecisionRequest,
)
from backend.app.services.leave_service import leave_service

router = APIRouter()

@router.get("/policies", response_model=List[LeavePolicyResponse], summary="List active leave policies")
async def list_policies(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LeavePolicy).where(
        LeavePolicy.organization_id == current_user.organization_id,
        LeavePolicy.is_active == True
    )
    policies = (await db.execute(stmt)).scalars().all()
    return list(policies)

@router.post("/policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED, summary="Create a leave policy")
async def create_policy(
    data: LeavePolicyCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    policy = LeavePolicy(
        **data.model_dump(),
        organization_id=current_user.organization_id,
        is_active=True
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return policy

@router.get("/balances/me", response_model=List[LeaveBalanceResponse], summary="Get current employee leave balances")
async def get_my_balances(
    year: Optional[int] = Query(None),
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await leave_service.get_employee_balances(
        db=db,
        employee_id=current_user.id,
        year=year
    )

@router.get("/requests/me", response_model=List[LeaveRequestResponse], summary="Get current employee leave history")
async def get_my_requests(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LeaveRequest, LeavePolicy.name).join(
        LeavePolicy, LeaveRequest.policy_id == LeavePolicy.id
    ).where(
        LeaveRequest.employee_id == current_user.id
    ).order_by(LeaveRequest.created_at.desc())

    results = (await db.execute(stmt)).all()
    responses = []
    for req, pol_name in results:
        resp = LeaveRequestResponse.model_validate(req)
        resp.policy_name = pol_name
        resp.employee_name = f"{current_user.first_name} {current_user.last_name}"
        responses.append(resp)
    return responses

@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED, summary="Submit a leave request")
async def submit_leave_request(
    data: LeaveRequestCreate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    req = await leave_service.submit_request(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id,
        data=data
    )
    resp = LeaveRequestResponse.model_validate(req)
    resp.employee_name = f"{current_user.first_name} {current_user.last_name}"
    return resp

@router.get("/requests/pending", response_model=List[LeaveRequestResponse], summary="List pending leave requests for review")
async def list_pending_requests(
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    query = select(LeaveRequest, LeavePolicy.name, Employee).join(
        LeavePolicy, LeaveRequest.policy_id == LeavePolicy.id
    ).join(
        Employee, LeaveRequest.employee_id == Employee.id
    ).where(
        LeaveRequest.organization_id == current_user.organization_id,
        LeaveRequest.status == LeaveStatus.PENDING
    )

    # People managers only review their direct reports
    if current_user.role == EmployeeRole.PEOPLE_MANAGER:
        query = query.where(Employee.manager_id == current_user.id)

    results = (await db.execute(query)).all()
    responses = []
    for req, pol_name, emp in results:
        resp = LeaveRequestResponse.model_validate(req)
        resp.policy_name = pol_name
        resp.employee_name = f"{emp.first_name} {emp.last_name}"
        responses.append(resp)
    return responses

@router.patch("/requests/{request_id}/decision", response_model=LeaveRequestResponse, summary="Approve or reject leave request")
async def decide_leave_request(
    request_id: uuid.UUID,
    data: LeaveDecisionRequest,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    req = await leave_service.process_decision(
        db=db,
        org_id=current_user.organization_id,
        approver_id=current_user.id,
        request_id=request_id,
        decision_data=data
    )
    return LeaveRequestResponse.model_validate(req)
