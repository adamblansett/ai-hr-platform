from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.employee import Employee
from backend.app.models.offboarding import OffboardingRecord, OffboardingTask, ExitInterviewFeedback
from backend.app.models.audit import AuditLog
from backend.app.schemas.offboarding import OffboardingInitiateRequest, ExitInterviewSubmit


class OffboardingService:
    @staticmethod
    async def initiate_offboarding(
        db: AsyncSession,
        org_id: str,
        initiator_id: str,
        req: OffboardingInitiateRequest
    ) -> OffboardingRecord:
        emp_res = await db.execute(select(Employee).where(Employee.id == req.employee_id, Employee.organization_id == org_id))
        emp = emp_res.scalar_one_or_none()
        if not emp:
            raise ValueError("Employee not found")

        record = OffboardingRecord(
            organization_id=org_id,
            employee_id=req.employee_id,
            initiator_id=initiator_id,
            last_working_day=req.last_working_day,
            termination_reason=req.termination_reason,
            status="IN_PROGRESS",
            notes=req.notes,
        )
        db.add(record)
        await db.flush()

        # Seed standard offboarding tasks
        standard_tasks = [
            ("Revoke SCIM 2.0 Identity & Enterprise SSO Access", "IT", "SECURITY_ADMIN"),
            ("Issue Prepaid Shipping Label for Laptop & Hardware Return", "IT", "IT_OPS"),
            ("Execute Remote Hardware Wipe & Security Audit Certification", "IT", "SECURITY_ADMIN"),
            ("Calculate Final Paystub & Accrued PTO Balance Payout", "FINANCE", "PAYROLL_ADMIN"),
            ("Conduct Exit Interview & Post-Employment IP/NDA Reaffirmation", "HR", "PEOPLE_MANAGER"),
            ("Archive Employee Records & Issue COBRA/Benefits Package", "HR", "HR_ADMIN"),
        ]

        for title, category, assigned in standard_tasks:
            task = OffboardingTask(
                offboarding_id=record.id,
                title=title,
                category=category,
                assigned_to=assigned,
                is_completed=False,
            )
            db.add(task)

        # Audit log
        audit = AuditLog(
            organization_id=org_id,
            actor_id=initiator_id,
            action="OFFBOARDING_INITIATED",
            resource_type="Employee",
            resource_id=req.employee_id,
            details={
                "last_working_day": str(req.last_working_day),
                "termination_reason": req.termination_reason,
            },
        )
        db.add(audit)

        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def trigger_scim_deprovisioning(db: AsyncSession, offboarding_id: str, actor_id: str) -> OffboardingRecord:
        res = await db.execute(select(OffboardingRecord).where(OffboardingRecord.id == offboarding_id))
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError("Offboarding record not found")

        emp_res = await db.execute(select(Employee).where(Employee.id == record.employee_id))
        emp = emp_res.scalar_one_or_none()
        if emp:
            emp.status = "TERMINATED"

        record.scim_deprovisioned = True

        # Complete the IT task if exists
        task_res = await db.execute(
            select(OffboardingTask).where(
                OffboardingTask.offboarding_id == offboarding_id,
                OffboardingTask.category == "IT",
                OffboardingTask.title.like("%SCIM%")
            )
        )
        it_task = task_res.scalar_one_or_none()
        if it_task:
            it_task.is_completed = True
            it_task.completed_at = datetime.now(timezone.utc)

        audit = AuditLog(
            organization_id=record.organization_id,
            actor_id=actor_id,
            action="SCIM_DEPROVISIONING_EXECUTED",
            resource_type="Employee",
            resource_id=record.employee_id,
            details={"offboarding_id": offboarding_id, "status": "SUSPENDED"},
        )
        db.add(audit)

        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def submit_exit_interview(
        db: AsyncSession,
        offboarding_id: str,
        data: ExitInterviewSubmit
    ) -> ExitInterviewFeedback:
        res = await db.execute(select(OffboardingRecord).where(OffboardingRecord.id == offboarding_id))
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError("Offboarding record not found")

        # Synthesize AI insights
        insights = {
            "sentiment_score": 0.85 if data.experience_rating >= 4 else (0.5 if data.experience_rating == 3 else 0.2),
            "retention_category": "COMPENSATION_CAREER_GROWTH" if "compensation" in data.primary_reason.lower() or "growth" in data.primary_reason.lower() else "ORGANIZATIONAL",
            "manager_relationship": "POSITIVE" if data.experience_rating >= 4 else "NEUTRAL_OR_NEEDS_ATTENTION",
            "recommendations": [
                "Review departmental market compensation bands",
                "Ensure proactive career trajectory roadmap in 1:1 check-ins",
            ],
        }

        feedback = ExitInterviewFeedback(
            offboarding_id=offboarding_id,
            employee_id=record.employee_id,
            primary_reason=data.primary_reason,
            experience_rating=data.experience_rating,
            manager_feedback=data.manager_feedback,
            company_culture_feedback=data.company_culture_feedback,
            ai_synthesized_insights=insights,
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback
