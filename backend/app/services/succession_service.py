from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.employee import Employee
from backend.app.models.compensation import CompensationPackage
from backend.app.models.succession import SkillCompetency, FlightRiskAssessment, InternalRequisition
from backend.app.schemas.succession import CandidateMatch


class SuccessionService:
    @staticmethod
    async def assess_flight_risk(db: AsyncSession, employee_id: str, org_id: str) -> FlightRiskAssessment:
        # Fetch employee
        emp_res = await db.execute(select(Employee).where(Employee.id == employee_id, Employee.organization_id == org_id))
        emp = emp_res.scalar_one_or_none()
        if not emp:
            raise ValueError("Employee not found")

        # Fetch comp
        comp_res = await db.execute(select(CompensationPackage).where(CompensationPackage.employee_id == employee_id))
        comp = comp_res.scalar_one_or_none()

        factors = []
        interventions = []
        score = 0.15  # baseline natural risk

        # Evaluate tenure
        hire_dt = emp.hire_date
        if hire_dt:
            # Handle date or datetime
            now_date = datetime.now(timezone.utc).date() if hasattr(hire_dt, "year") and not hasattr(hire_dt, "hour") else datetime.now(timezone.utc)
            tenure_days = (now_date - hire_dt).days if hasattr(hire_dt, "year") else 365
            tenure_years = tenure_days / 365.25
            if tenure_years >= 2.5:
                score += 0.25
                factors.append(f"Extended tenure in current role ({tenure_years:.1f} yrs)")
                interventions.append("Plan lateral rotation or promotion evaluation")
            elif tenure_years <= 0.5:
                score += 0.10
                factors.append("Early onboarding transition window")
                interventions.append("Schedule 90-day manager pulse check")

        # Evaluate compensation
        if comp:
            if comp.base_salary < 85000:
                score += 0.20
                factors.append("Base salary below upper market benchmark")
                interventions.append("Conduct spot compensation adjustment")
        else:
            score += 0.10
            factors.append("No active benchmarked compensation package recorded")
            interventions.append("Formalize compensation package and review cycle")

        # Cap score
        score = min(max(score, 0.05), 0.95)

        if score >= 0.70:
            level = "CRITICAL"
        elif score >= 0.50:
            level = "HIGH"
        elif score >= 0.30:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Check existing assessment or create
        existing_res = await db.execute(select(FlightRiskAssessment).where(FlightRiskAssessment.employee_id == employee_id))
        record = existing_res.scalar_one_or_none()
        if not record:
            record = FlightRiskAssessment(
                organization_id=org_id,
                employee_id=employee_id,
                risk_score=round(score, 2),
                risk_level=level,
                contributing_factors=factors,
                recommended_interventions=interventions,
                evaluated_at=datetime.now(timezone.utc),
            )
            db.add(record)
        else:
            record.risk_score = round(score, 2)
            record.risk_level = level
            record.contributing_factors = factors
            record.recommended_interventions = interventions
            record.evaluated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def match_candidates(db: AsyncSession, req_id: str, org_id: str) -> List[CandidateMatch]:
        req_res = await db.execute(select(InternalRequisition).where(InternalRequisition.id == req_id, InternalRequisition.organization_id == org_id))
        req = req_res.scalar_one_or_none()
        if not req:
            raise ValueError("Requisition not found")

        required_skills = [s.strip().lower() for s in (req.required_skills or [])]

        # Fetch active employees
        emps_res = await db.execute(select(Employee).where(Employee.organization_id == org_id, Employee.status == "ACTIVE"))
        employees = emps_res.scalars().all()

        matches = []
        for emp in employees:
            skills_res = await db.execute(select(SkillCompetency).where(SkillCompetency.employee_id == emp.id))
            emp_skills = [s.skill_name.strip().lower() for s in skills_res.scalars().all()]
            
            matching = [s for s in required_skills if s in emp_skills]
            missing = [s for s in required_skills if s not in emp_skills]
            score_pct = (len(matching) / len(required_skills) * 100.0) if required_skills else 100.0

            matches.append(CandidateMatch(
                employee_id=emp.id,
                employee_name=f"{emp.first_name} {emp.last_name}",
                department=emp.department or "General",
                current_title=emp.job_title or "Specialist",
                match_score_percent=round(score_pct, 1),
                matching_skills=matching,
                missing_skills=missing,
            ))

        matches.sort(key=lambda x: x.match_score_percent, reverse=True)
        return matches
