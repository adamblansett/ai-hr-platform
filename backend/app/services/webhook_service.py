import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.models.organization import Organization
from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus
from backend.app.models.onboarding import OnboardingTask, OnboardingCategory, OnboardingStatus
from backend.app.models.audit import AuditLog
from backend.app.schemas.webhook import RecruiterOfferAcceptedWebhook, RecruiterWebhookResponse
from backend.app.services.provisioning import get_provisioning_adapter
from backend.app.services.pii_scrubber import PIIScrubber

class WebhookService:
    @staticmethod
    def verify_signature(raw_body: bytes, signature_header: Optional[str], secret: Optional[str] = None) -> bool:
        """
        Validates HMAC-SHA256 signature from X-Recruiter-Signature header.
        Format expected: 'sha256=<hex_digest>' or bare hex digest.
        """
        if not signature_header:
            return False

        shared_secret = secret or settings.RECRUITER_WEBHOOK_SECRET
        expected_sig = hmac.new(
            shared_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        provided_sig = signature_header
        if signature_header.startswith("sha256="):
            provided_sig = signature_header.split("sha256=")[-1]

        return hmac.compare_digest(expected_sig, provided_sig)

    @staticmethod
    async def process_offer_accepted(
        db: AsyncSession,
        payload: RecruiterOfferAcceptedWebhook,
        ip_address: Optional[str] = None
    ) -> RecruiterWebhookResponse:
        cand = payload.candidate
        org_id = payload.organization_id

        # 1. Validate Organization exists
        org_stmt = select(Organization).where(Organization.id == org_id)
        org = (await db.execute(org_stmt)).scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization {org_id} not found"
            )

        # 2. Check if candidate or employee already exists (idempotency check)
        emp_stmt = select(Employee).where(Employee.email == cand.email)
        existing_emp = (await db.execute(emp_stmt)).scalar_one_or_none()
        if existing_emp:
            return RecruiterWebhookResponse(
                success=True,
                message=f"Candidate with email {cand.email} already exists in organization",
                employee_id=existing_emp.id,
                onboarding_tasks_created=0
            )

        # 3. Look up Manager if manager_email supplied
        manager_id: Optional[uuid.UUID] = None
        if cand.manager_email:
            mgr_stmt = select(Employee).where(
                Employee.email == cand.manager_email,
                Employee.organization_id == org_id
            )
            manager = (await db.execute(mgr_stmt)).scalar_one_or_none()
            if manager:
                manager_id = manager.id

        # 4. Provision Employee Record in status ONBOARDING
        temp_pass = f"Welcome!{uuid.uuid4().hex[:8]}"
        new_employee = Employee(
            organization_id=org_id,
            email=cand.email,
            hashed_password=get_password_hash(temp_pass),
            first_name=cand.first_name,
            last_name=cand.last_name,
            phone_number=cand.phone,
            role=EmployeeRole.EMPLOYEE,
            status=EmploymentStatus.ONBOARDING,
            employment_type=cand.employment_type,
            department=cand.department,
            job_title=cand.job_title,
            manager_id=manager_id,
            hire_date=cand.hire_date,
            custom_attributes={
                "recruiter_candidate_id": cand.recruiter_candidate_id,
                "offer_signed_doc_url": cand.offer_signed_doc_url,
                **cand.custom_fields
            }
        )
        db.add(new_employee)
        await db.flush() # Populate new_employee.id

        # 5. Generate Standard Onboarding Tasks Checklist
        default_tasks = [
            OnboardingTask(
                organization_id=org_id,
                employee_id=new_employee.id,
                recruiter_candidate_id=cand.recruiter_candidate_id,
                offer_acceptance_reference=payload.event_id,
                title="Submit I-9 and W-4 Tax Documentation",
                description="Upload government ID and federal withholding forms for compliance verification.",
                category=OnboardingCategory.DOCUMENTATION,
                status=OnboardingStatus.PENDING,
                due_date=cand.hire_date,
                assigned_to_role="EMPLOYEE",
                document_url=cand.offer_signed_doc_url
            ),
            OnboardingTask(
                organization_id=org_id,
                employee_id=new_employee.id,
                recruiter_candidate_id=cand.recruiter_candidate_id,
                offer_acceptance_reference=payload.event_id,
                title="Complete Emergency Contacts & Profile Details",
                description="Fill in emergency contacts, preferred name, and personal communications info.",
                category=OnboardingCategory.DOCUMENTATION,
                status=OnboardingStatus.PENDING,
                due_date=cand.hire_date,
                assigned_to_role="EMPLOYEE"
            ),
            OnboardingTask(
                organization_id=org_id,
                employee_id=new_employee.id,
                recruiter_candidate_id=cand.recruiter_candidate_id,
                offer_acceptance_reference=payload.event_id,
                title="Provision Corporate Laptop & Hardware Dispatch",
                description="Configure workstation image, security keys, and arrange courier dispatch.",
                category=OnboardingCategory.EQUIPMENT,
                status=OnboardingStatus.PENDING,
                due_date=cand.hire_date,
                assigned_to_role="IT_ADMIN"
            ),
            OnboardingTask(
                organization_id=org_id,
                employee_id=new_employee.id,
                recruiter_candidate_id=cand.recruiter_candidate_id,
                offer_acceptance_reference=payload.event_id,
                title="Review & Acknowledge Employee Handbook & Code of Conduct",
                description="Read corporate policies, information security guidelines, and electronically sign acknowledgment.",
                category=OnboardingCategory.COMPLIANCE,
                status=OnboardingStatus.PENDING,
                due_date=cand.hire_date,
                assigned_to_role="EMPLOYEE"
            )
        ]
        db.add_all(default_tasks)

        # 6. Dispatch IdP Provisioning via configured adapter (Mock by default)
        idp_adapter_type = org.settings.get("idp_provider", "mock")
        idp_config = org.settings.get("idp_config", {})
        adapter = get_provisioning_adapter(idp_adapter_type, idp_config)
        
        prov_result = await adapter.provision_employee({
            "email": cand.email,
            "first_name": cand.first_name,
            "last_name": cand.last_name,
            "department": cand.department,
            "job_title": cand.job_title,
            "phone_number": cand.phone
        })

        # 7. Record Immutable Audit Log (with PII Redacted)
        audit_details = {
            "event_id": payload.event_id,
            "event_type": payload.event_type,
            "recruiter_candidate_id": cand.recruiter_candidate_id,
            "email_masked": f"{cand.email[:2]}***@{cand.email.split('@')[-1]}",
            "department": cand.department,
            "job_title": cand.job_title,
            "tasks_seeded": len(default_tasks),
            "idp_provider": idp_adapter_type,
            "idp_status": prov_result.status.value,
            "external_idp_id": prov_result.external_id
        }

        audit_log = AuditLog(
            organization_id=org_id,
            actor_id=None, # System / webhook triggered
            action="ONBOARDING_OFFER_ACCEPTED_WEBHOOK",
            entity_type="Employee",
            entity_id=str(new_employee.id),
            details=audit_details,
            ip_address=ip_address,
            pii_redacted=True
        )
        db.add(audit_log)

        # Commit atomic transaction
        await db.commit()
        await db.refresh(new_employee)

        return RecruiterWebhookResponse(
            success=True,
            message="Candidate successfully transitioned into employee onboarding workflow",
            employee_id=new_employee.id,
            onboarding_tasks_created=len(default_tasks),
            external_idp_id=prov_result.external_id
        )

webhook_service = WebhookService()
