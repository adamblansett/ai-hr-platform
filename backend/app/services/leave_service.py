import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.leave import LeavePolicy, LeaveBalance, LeaveRequest, LeaveStatus, LeaveType
from backend.app.models.employee import Employee
from backend.app.models.audit import AuditLog
from backend.app.schemas.leave import (
    LeavePolicyCreate,
    LeaveRequestCreate,
    LeaveDecisionRequest,
    LeaveBalanceResponse,
    LeaveRequestResponse,
)

class LeaveService:
    @staticmethod
    def calculate_business_days(start_date: date, end_date: date) -> float:
        """
        Calculates working weekdays between start and end dates (inclusive).
        """
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date cannot be prior to start date"
            )

        current = start_date
        days = 0.0
        while current <= end_date:
            if current.weekday() < 5: # Mon-Fri
                days += 1.0
            current += timedelta(days=1)
        return max(days, 1.0)

    @staticmethod
    async def get_or_create_balance(
        db: AsyncSession,
        employee_id: uuid.UUID,
        policy_id: uuid.UUID,
        year: int
    ) -> LeaveBalance:
        stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.policy_id == policy_id,
            LeaveBalance.year == year
        )
        bal = (await db.execute(stmt)).scalar_one_or_none()
        if not bal:
            # Look up policy to seed default initial accrual
            p_stmt = select(LeavePolicy).where(LeavePolicy.id == policy_id)
            policy = (await db.execute(p_stmt)).scalar_one_or_none()
            initial_accrued = policy.annual_days_allowed if policy else 15.0

            bal = LeaveBalance(
                employee_id=employee_id,
                policy_id=policy_id,
                year=year,
                accrued_days=initial_accrued,
                used_days=0.0,
                carried_over_days=0.0
            )
            db.add(bal)
            await db.flush()
        return bal

    @staticmethod
    async def detect_team_conflicts(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        start_date: date,
        end_date: date
    ) -> bool:
        """
        Checks if another active employee in the same department has an approved leave
        overlapping the requested dates.
        """
        emp_stmt = select(Employee).where(Employee.id == employee_id)
        emp = (await db.execute(emp_stmt)).scalar_one_or_none()
        if not emp:
            return False

        # Find colleagues in same department with approved leaves
        query = select(LeaveRequest).join(
            Employee, LeaveRequest.employee_id == Employee.id
        ).where(
            LeaveRequest.organization_id == org_id,
            LeaveRequest.employee_id != employee_id,
            Employee.department == emp.department,
            LeaveRequest.status == LeaveStatus.APPROVED,
            or_(
                and_(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= start_date)
            )
        )
        overlapping = (await db.execute(query)).scalars().all()
        return len(overlapping) > 0

    @staticmethod
    async def submit_request(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: LeaveRequestCreate
    ) -> LeaveRequest:
        total_days = LeaveService.calculate_business_days(data.start_date, data.end_date)
        current_year = data.start_date.year

        # Check balance
        balance = await LeaveService.get_or_create_balance(db, employee_id, data.policy_id, current_year)
        if balance.remaining_days < total_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Requested {total_days} days, remaining {balance.remaining_days} days."
            )

        # Detect team calendar overlap conflicts
        conflict_flag = await LeaveService.detect_team_conflicts(
            db, org_id, employee_id, data.start_date, data.end_date
        )

        leave_req = LeaveRequest(
            organization_id=org_id,
            employee_id=employee_id,
            policy_id=data.policy_id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_days=total_days,
            reason=data.reason,
            status=LeaveStatus.PENDING,
            calendar_conflict_flag=conflict_flag
        )
        db.add(leave_req)
        await db.commit()
        await db.refresh(leave_req)
        return leave_req

    @staticmethod
    async def process_decision(
        db: AsyncSession,
        org_id: uuid.UUID,
        approver_id: uuid.UUID,
        request_id: uuid.UUID,
        decision_data: LeaveDecisionRequest
    ) -> LeaveRequest:
        stmt = select(LeaveRequest).where(
            LeaveRequest.id == request_id,
            LeaveRequest.organization_id == org_id
        )
        req = (await db.execute(stmt)).scalar_one_or_none()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

        if req.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot decide on leave request with status {req.status.value}"
            )

        req.status = decision_data.status
        req.decision_reason = decision_data.decision_reason
        req.approver_id = approver_id

        # If approved, deduct balance
        if decision_data.status == LeaveStatus.APPROVED:
            bal = await LeaveService.get_or_create_balance(
                db, req.employee_id, req.policy_id, req.start_date.year
            )
            bal.used_days += req.total_days

        # Log audit trail
        audit = AuditLog(
            organization_id=org_id,
            actor_id=approver_id,
            action=f"LEAVE_REQUEST_{decision_data.status.value}",
            entity_type="LeaveRequest",
            entity_id=str(req.id),
            details={
                "employee_id": str(req.employee_id),
                "total_days": req.total_days,
                "reason": decision_data.decision_reason
            },
            pii_redacted=True
        )
        db.add(audit)

        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def get_employee_balances(
        db: AsyncSession,
        employee_id: uuid.UUID,
        year: Optional[int] = None
    ) -> List[LeaveBalanceResponse]:
        query_year = year or date.today().year

        stmt = select(LeaveBalance, LeavePolicy).join(
            LeavePolicy, LeaveBalance.policy_id == LeavePolicy.id
        ).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == query_year
        )
        results = (await db.execute(stmt)).all()

        balances = []
        for bal, pol in results:
            balances.append(
                LeaveBalanceResponse(
                    id=bal.id,
                    employee_id=bal.employee_id,
                    policy_id=bal.policy_id,
                    policy_name=pol.name,
                    leave_type=pol.leave_type,
                    year=bal.year,
                    accrued_days=bal.accrued_days,
                    used_days=bal.used_days,
                    carried_over_days=bal.carried_over_days,
                    remaining_days=bal.remaining_days
                )
            )
        return balances

leave_service = LeaveService()
