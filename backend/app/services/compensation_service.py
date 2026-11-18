import uuid
from datetime import date, timedelta
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.compensation import (
    CompensationPackage,
    EquityGrant,
    PaystubRecord,
    PayFrequency,
    EquityGrantType,
)
from backend.app.models.employee import Employee
from backend.app.schemas.compensation import (
    CompensationPackageCreate,
    EquityGrantCreate,
    VestingScheduleMilestone,
    EquityGrantResponse,
    PaystubResponse,
    EmployeeTotalRewardsSummary,
)

class CompensationService:
    @staticmethod
    def calculate_vesting_schedule(grant: EquityGrant, as_of_date: Optional[date] = None) -> Tuple[int, int, List[VestingScheduleMilestone]]:
        target_date = as_of_date or date.today()
        milestones: List[VestingScheduleMilestone] = []

        start = grant.vesting_start_date
        total = grant.total_shares
        cliff_m = grant.cliff_months
        total_m = grant.vesting_duration_months

        # Cliff date (1 year)
        cliff_date = start + timedelta(days=int(cliff_m * 30.4375))
        cliff_shares = int(total * (cliff_m / total_m))

        milestones.append(
            VestingScheduleMilestone(
                vest_date=cliff_date,
                shares_vesting=cliff_shares,
                cumulative_vested_shares=cliff_shares,
                vesting_percentage=round((cliff_shares / total) * 100, 1),
                is_cliff=True
            )
        )

        remaining_shares = total - cliff_shares
        remaining_months = total_m - cliff_m
        monthly_shares = int(remaining_shares / remaining_months) if remaining_months > 0 else 0

        cum = cliff_shares
        for m in range(cliff_m + 1, total_m + 1):
            vest_d = start + timedelta(days=int(m * 30.4375))
            vesting_amount = monthly_shares if m < total_m else (total - cum)
            cum += vesting_amount
            milestones.append(
                VestingScheduleMilestone(
                    vest_date=vest_d,
                    shares_vesting=vesting_amount,
                    cumulative_vested_shares=cum,
                    vesting_percentage=round((cum / total) * 100, 1),
                    is_cliff=False
                )
            )

        # Calculate currently vested
        vested_now = 0
        if target_date >= cliff_date:
            for ms in milestones:
                if ms.vest_date <= target_date:
                    vested_now = ms.cumulative_vested_shares
                else:
                    break

        unvested_now = max(total - vested_now, 0)
        return vested_now, unvested_now, milestones

    @staticmethod
    async def create_or_update_package(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: CompensationPackageCreate
    ) -> CompensationPackage:
        # Check active package
        stmt = select(CompensationPackage).where(
            CompensationPackage.employee_id == data.employee_id,
            CompensationPackage.organization_id == org_id,
            CompensationPackage.is_active == True
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.is_active = False

        pkg = CompensationPackage(
            organization_id=org_id,
            employee_id=data.employee_id,
            base_salary=data.base_salary,
            currency=data.currency,
            effective_date=data.effective_date,
            pay_frequency=data.pay_frequency,
            target_bonus_percentage=data.target_bonus_percentage,
            is_active=True
        )
        db.add(pkg)
        await db.commit()
        await db.refresh(pkg)
        return pkg

    @staticmethod
    async def create_equity_grant(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: EquityGrantCreate
    ) -> EquityGrant:
        grant = EquityGrant(
            organization_id=org_id,
            employee_id=data.employee_id,
            grant_number=data.grant_number,
            grant_type=data.grant_type,
            total_shares=data.total_shares,
            strike_price=data.strike_price,
            grant_date=data.grant_date,
            vesting_start_date=data.vesting_start_date,
            cliff_months=data.cliff_months,
            vesting_duration_months=data.vesting_duration_months
        )
        db.add(grant)
        await db.commit()
        await db.refresh(grant)
        return grant

    @staticmethod
    async def get_total_rewards(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID
    ) -> EmployeeTotalRewardsSummary:
        # 1. Compensation Package
        p_stmt = select(CompensationPackage).where(
            CompensationPackage.employee_id == employee_id,
            CompensationPackage.organization_id == org_id,
            CompensationPackage.is_active == True
        )
        pkg = (await db.execute(p_stmt)).scalar_one_or_none()
        base_salary = pkg.base_salary if pkg else 0.0
        currency = pkg.currency if pkg else "USD"
        bonus_pct = pkg.target_bonus_percentage if pkg else 0.0
        bonus_val = base_salary * (bonus_pct / 100.0)

        # 2. Equity Grants
        e_stmt = select(EquityGrant).where(
            EquityGrant.employee_id == employee_id,
            EquityGrant.organization_id == org_id
        ).order_by(EquityGrant.grant_date.desc())
        grants = (await db.execute(e_stmt)).scalars().all()

        grant_responses = []
        total_granted = 0
        total_vested = 0
        for g in grants:
            v_now, unv_now, sched = CompensationService.calculate_vesting_schedule(g)
            total_granted += g.total_shares
            total_vested += v_now
            grant_responses.append(
                EquityGrantResponse(
                    id=g.id,
                    organization_id=g.organization_id,
                    employee_id=g.employee_id,
                    grant_number=g.grant_number,
                    grant_type=g.grant_type,
                    total_shares=g.total_shares,
                    strike_price=g.strike_price,
                    grant_date=g.grant_date,
                    vesting_start_date=g.vesting_start_date,
                    cliff_months=g.cliff_months,
                    vesting_duration_months=g.vesting_duration_months,
                    vested_shares_to_date=v_now,
                    unvested_shares=unv_now,
                    schedule_preview=sched[:6] # First 6 milestones for preview
                )
            )

        # 3. Paystubs
        ps_stmt = select(PaystubRecord).where(
            PaystubRecord.employee_id == employee_id,
            PaystubRecord.organization_id == org_id
        ).order_by(PaystubRecord.pay_date.desc()).limit(12)
        paystubs = (await db.execute(ps_stmt)).scalars().all()
        paystub_responses = [PaystubResponse.model_validate(ps) for ps in paystubs]

        return EmployeeTotalRewardsSummary(
            employee_id=employee_id,
            base_salary=base_salary,
            currency=currency,
            target_bonus_annual=bonus_val,
            total_cash_compensation=base_salary + bonus_val,
            equity_grants_count=len(grants),
            total_granted_shares=total_granted,
            total_vested_shares=total_vested,
            equity_grants=grant_responses,
            recent_paystubs=paystub_responses
        )

    @staticmethod
    async def generate_payroll_cycle(
        db: AsyncSession,
        org_id: uuid.UUID,
        pay_period_start: date,
        pay_period_end: date,
        pay_date: date
    ) -> List[PaystubRecord]:
        """
        Executes a payroll cycle for all active employees with compensation packages.
        """
        stmt = select(CompensationPackage, Employee).join(
            Employee, CompensationPackage.employee_id == Employee.id
        ).where(
            CompensationPackage.organization_id == org_id,
            CompensationPackage.is_active == True
        )
        packages = (await db.execute(stmt)).all()

        generated = []
        for pkg, emp in packages:
            # Calculate periods per year
            periods_per_year = 26 if pkg.pay_frequency == PayFrequency.BI_WEEKLY else (12 if pkg.pay_frequency == PayFrequency.MONTHLY else 52)
            gross = round(pkg.base_salary / periods_per_year, 2)

            # Simulated payroll deductions
            fed_tax = round(gross * 0.22, 2)
            fica_tax = round(gross * 0.062, 2)
            medicare = round(gross * 0.0145, 2)
            health_benefit = 150.00
            total_deductions = fed_tax + fica_tax + medicare + health_benefit
            net = round(gross - total_deductions, 2)

            stub = PaystubRecord(
                organization_id=org_id,
                employee_id=emp.id,
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end,
                pay_date=pay_date,
                gross_amount=gross,
                net_amount=net,
                tax_withholdings={
                    "federal_income_tax": fed_tax,
                    "social_security_fica": fica_tax,
                    "medicare": medicare
                },
                benefit_deductions={
                    "medical_dental_vision": health_benefit
                },
                pdf_url=f"https://storage.internal/payroll/{org_id}/{emp.id}/{pay_date.isoformat()}_paystub.pdf"
            )
            db.add(stub)
            generated.append(stub)

        await db.commit()
        return generated

compensation_service = CompensationService()
