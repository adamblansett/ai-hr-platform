import uuid
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.schemas.compensation import (
    CompensationPackageCreate,
    CompensationPackageResponse,
    EquityGrantCreate,
    EquityGrantResponse,
    PaystubResponse,
    EmployeeTotalRewardsSummary,
)
from backend.app.services.compensation_service import compensation_service

router = APIRouter()

@router.get("/me", response_model=EmployeeTotalRewardsSummary, summary="Get own total compensation, equity vesting & paystubs")
async def get_my_total_rewards(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await compensation_service.get_total_rewards(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id
    )

@router.get("/employee/{employee_id}", response_model=EmployeeTotalRewardsSummary, summary="View employee total rewards (HR Admin & Manager)")
async def get_employee_total_rewards(
    employee_id: uuid.UUID,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    return await compensation_service.get_total_rewards(
        db=db,
        org_id=current_user.organization_id,
        employee_id=employee_id
    )

@router.post("/packages", response_model=CompensationPackageResponse, status_code=status.HTTP_201_CREATED, summary="Create or update compensation package")
async def create_compensation_package(
    data: CompensationPackageCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    pkg = await compensation_service.create_or_update_package(
        db=db,
        org_id=current_user.organization_id,
        data=data
    )
    return CompensationPackageResponse.model_validate(pkg)

@router.post("/equity", response_model=EquityGrantResponse, status_code=status.HTTP_201_CREATED, summary="Issue an equity grant")
async def issue_equity_grant(
    data: EquityGrantCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    grant = await compensation_service.create_equity_grant(
        db=db,
        org_id=current_user.organization_id,
        data=data
    )
    v_now, unv_now, sched = compensation_service.calculate_vesting_schedule(grant)
    return EquityGrantResponse(
        id=grant.id,
        organization_id=grant.organization_id,
        employee_id=grant.employee_id,
        grant_number=grant.grant_number,
        grant_type=grant.grant_type,
        total_shares=grant.total_shares,
        strike_price=grant.strike_price,
        grant_date=grant.grant_date,
        vesting_start_date=grant.vesting_start_date,
        cliff_months=grant.cliff_months,
        vesting_duration_months=grant.vesting_duration_months,
        vested_shares_to_date=v_now,
        unvested_shares=unv_now,
        schedule_preview=sched[:6]
    )

@router.post("/paystubs/run-payroll", response_model=List[PaystubResponse], summary="Execute an organizational payroll cycle")
async def run_payroll_cycle(
    period_start: date = Query(...),
    period_end: date = Query(...),
    pay_date: date = Query(...),
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stubs = await compensation_service.generate_payroll_cycle(
        db=db,
        org_id=current_user.organization_id,
        pay_period_start=period_start,
        pay_period_end=period_end,
        pay_date=pay_date
    )
    return [PaystubResponse.model_validate(s) for s in stubs]
