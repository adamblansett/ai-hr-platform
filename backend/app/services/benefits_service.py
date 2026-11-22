from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.benefits import BenefitPlan, EmployeeBenefitElection
from backend.app.schemas.benefits import BenefitElectionCreate, BenefitsAdvisorQuery, BenefitsAdvisorResponse


class BenefitsService:
    @staticmethod
    async def get_or_seed_plans(db: AsyncSession, org_id: str) -> List[BenefitPlan]:
        res = await db.execute(select(BenefitPlan).where(BenefitPlan.organization_id == org_id))
        plans = res.scalars().all()
        if plans:
            return list(plans)

        # Seed standard enterprise benefit plans
        defaults = [
            BenefitPlan(
                organization_id=org_id,
                plan_name="Acme Anthem Platinum PPO 500",
                plan_type="MEDICAL",
                provider="Anthem Blue Cross",
                tier_name="PPO",
                monthly_employee_premium=135.0,
                monthly_employer_contribution=540.0,
                annual_deductible=500.0,
                out_of_pocket_max=3000.0,
                summary_of_benefits="Comprehensive low-deductible network coverage. $20 primary care copay, $40 specialist.",
            ),
            BenefitPlan(
                organization_id=org_id,
                plan_name="Acme Anthem HDHP with HSA Contribution",
                plan_type="MEDICAL",
                provider="Anthem Blue Cross",
                tier_name="HDHP",
                monthly_employee_premium=45.0,
                monthly_employer_contribution=480.0,
                annual_deductible=2000.0,
                out_of_pocket_max=5000.0,
                summary_of_benefits="High-deductible healthcare plan paired with a $1,000 annual employer HSA seeding contribution.",
            ),
            BenefitPlan(
                organization_id=org_id,
                plan_name="Delta Dental Premier PPO Plus",
                plan_type="DENTAL",
                provider="Delta Dental",
                tier_name="PPO",
                monthly_employee_premium=22.0,
                monthly_employer_contribution=68.0,
                annual_deductible=50.0,
                out_of_pocket_max=2000.0,
                summary_of_benefits="100% preventative cleanings covered twice annually. 80% basic procedures, 50% major restorative.",
            ),
            BenefitPlan(
                organization_id=org_id,
                plan_name="VSP Vision Choice Standard",
                plan_type="VISION",
                provider="VSP",
                tier_name="VISION",
                monthly_employee_premium=8.50,
                monthly_employer_contribution=25.0,
                annual_deductible=10.0,
                out_of_pocket_max=500.0,
                summary_of_benefits="$10 annual eye exam copay, $200 frame allowance every 12 months with prescription lenses.",
            ),
        ]
        for p in defaults:
            db.add(p)
        await db.commit()
        return defaults

    @staticmethod
    async def enroll_employee(
        db: AsyncSession,
        org_id: str,
        employee_id: str,
        data: BenefitElectionCreate
    ) -> EmployeeBenefitElection:
        p_res = await db.execute(select(BenefitPlan).where(BenefitPlan.id == data.plan_id))
        plan = p_res.scalar_one_or_none()
        if not plan:
            raise ValueError("Benefit plan not found")

        # Multiplier based on tier
        multiplier_map = {
            "EMPLOYEE_ONLY": 1.0,
            "EMPLOYEE_PLUS_SPOUSE": 1.8,
            "EMPLOYEE_PLUS_CHILDREN": 1.7,
            "FAMILY": 2.5,
        }
        mult = multiplier_map.get(data.coverage_tier, 1.0)
        emp_cost = round(plan.monthly_employee_premium * mult, 2)
        co_cost = round(plan.monthly_employer_contribution * mult, 2)

        # Deactivate previous active election for this plan type
        existing_res = await db.execute(
            select(EmployeeBenefitElection).join(BenefitPlan).where(
                EmployeeBenefitElection.employee_id == employee_id,
                BenefitPlan.plan_type == plan.plan_type,
                EmployeeBenefitElection.status == "ACTIVE"
            )
        )
        existing = existing_res.scalars().all()
        for e in existing:
            e.status = "SUPERSEDED"

        election = EmployeeBenefitElection(
            organization_id=org_id,
            employee_id=employee_id,
            plan_id=data.plan_id,
            coverage_tier=data.coverage_tier,
            effective_date=data.effective_date,
            employee_monthly_cost=emp_cost,
            employer_monthly_cost=co_cost,
            status="ACTIVE",
        )
        db.add(election)
        await db.commit()
        await db.refresh(election)
        election.plan_name = plan.plan_name
        election.plan_type = plan.plan_type
        return election

    @staticmethod
    def advise_on_benefits(query: BenefitsAdvisorQuery) -> BenefitsAdvisorResponse:
        q_lower = query.question.lower()
        family = query.family_members_count or 1
        chronic = query.has_chronic_needs or False

        if "hsa" in q_lower or "tax" in q_lower or (family == 1 and not chronic):
            recommended = "Acme Anthem HDHP with HSA Contribution"
            reason = "Optimal choice for lower monthly payroll deductions with tax-advantaged HSA growth ($1,000 employer seed)."
            annual_cost = 45.0 * 12
            highlights = [
                "$1,000 employer HSA annual contribution",
                "Triple-tax advantaged medical savings",
                "100% preventative care coverage before deductible",
            ]
        else:
            recommended = "Acme Anthem Platinum PPO 500"
            reason = "Recommended for predictable out-of-pocket expenses, lower $500 deductible, and fixed specialist copays for family coverage."
            annual_cost = 135.0 * (2.5 if family >= 3 else 1.0) * 12
            highlights = [
                "Low $500 annual deductible",
                "$20 primary care copay & $40 specialist copay",
                "Wide in-network physician and hospital access nationwide",
            ]

        return BenefitsAdvisorResponse(
            question=query.question,
            recommended_plan_name=recommended,
            recommendation_reason=reason,
            estimated_annual_employee_cost=round(annual_cost, 2),
            coverage_highlights=highlights,
        )
