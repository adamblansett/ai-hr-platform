import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.organization import Organization
from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus, EmploymentType
from backend.app.models.leave import LeavePolicy, LeaveBalance, LeaveType
from backend.app.models.onboarding import OnboardingTask, OnboardingCategory, OnboardingStatus
from backend.app.models.policy import PolicyDocument
from backend.app.models.performance import PerformanceCycle, GoalOKR, CycleStatus, GoalStatus
from backend.app.models.audit import AuditLog

DEMO_ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
COMMON_PASSWORD = "Password123!"

async def seed_database():
    print("🌱 Starting database seeding for ai-hr-platform...")
    async with AsyncSessionLocal() as db:
        # 1. Organization
        org_stmt = select(Organization).where(Organization.id == DEMO_ORG_ID)
        org = (await db.execute(org_stmt)).scalar_one_or_none()
        if not org:
            org = Organization(
                id=DEMO_ORG_ID,
                name="Acme Innovations Inc.",
                slug="acme-innovations",
                domain="acme.corp",
                is_active=True,
                settings={"idp_provider": "mock", "timezone": "America/New_York"}
            )
            db.add(org)
            await db.flush()
            print("  Created organization: Acme Innovations Inc.")
        else:
            print("  Organization already exists, skipping...")

        # 2. Leave Policies
        policies_data = [
            ("Paid Time Off (PTO)", LeaveType.PTO, 15.0, 1.25, 5.0),
            ("Sick & Medical Leave", LeaveType.SICK, 10.0, 0.83, 3.0),
            ("Paid Parental Leave", LeaveType.PARENTAL, 60.0, 0.0, 0.0),
        ]
        created_policies = {}
        for name, ltype, annual, monthly, carry in policies_data:
            stmt = select(LeavePolicy).where(
                LeavePolicy.organization_id == DEMO_ORG_ID,
                LeavePolicy.name == name
            )
            pol = (await db.execute(stmt)).scalar_one_or_none()
            if not pol:
                pol = LeavePolicy(
                    organization_id=DEMO_ORG_ID,
                    name=name,
                    leave_type=ltype,
                    annual_days_allowed=annual,
                    accrual_rate_per_month=monthly,
                    max_carryover_days=carry,
                    requires_approval=True,
                    is_active=True
                )
                db.add(pol)
                await db.flush()
                print(f"  Created leave policy: {name}")
            created_policies[ltype] = pol

        # 3. Employees
        hashed_pw = get_password_hash(COMMON_PASSWORD)

        # Admin
        admin_stmt = select(Employee).where(Employee.email == "admin@acme.corp")
        admin = (await db.execute(admin_stmt)).scalar_one_or_none()
        if not admin:
            admin = Employee(
                organization_id=DEMO_ORG_ID,
                email="admin@acme.corp",
                hashed_password=hashed_pw,
                first_name="Victoria",
                last_name="Sterling",
                role=EmployeeRole.SUPER_ADMIN,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="Human Resources",
                job_title="VP of People Operations",
                hire_date=date(2023, 1, 15),
                custom_attributes={"is_demo_account": True}
            )
            db.add(admin)
            await db.flush()
            print("  Created employee: admin@acme.corp (SUPER_ADMIN)")

        # People Manager
        mgr_stmt = select(Employee).where(Employee.email == "manager.sarah@acme.corp")
        manager = (await db.execute(mgr_stmt)).scalar_one_or_none()
        if not manager:
            manager = Employee(
                organization_id=DEMO_ORG_ID,
                email="manager.sarah@acme.corp",
                hashed_password=hashed_pw,
                first_name="Sarah",
                last_name="Connor",
                role=EmployeeRole.PEOPLE_MANAGER,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="Engineering",
                job_title="Engineering Director",
                manager_id=admin.id,
                hire_date=date(2023, 6, 1),
                custom_attributes={"team": "Platform & AI"}
            )
            db.add(manager)
            await db.flush()
            print("  Created employee: manager.sarah@acme.corp (PEOPLE_MANAGER)")

        # Senior Engineer (Active)
        eng_stmt = select(Employee).where(Employee.email == "engineer.alex@acme.corp")
        engineer = (await db.execute(eng_stmt)).scalar_one_or_none()
        if not engineer:
            engineer = Employee(
                organization_id=DEMO_ORG_ID,
                email="engineer.alex@acme.corp",
                hashed_password=hashed_pw,
                first_name="Alex",
                last_name="Chen",
                role=EmployeeRole.EMPLOYEE,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="Engineering",
                job_title="Senior AI Infrastructure Engineer",
                manager_id=manager.id,
                hire_date=date(2024, 2, 1),
                custom_attributes={"github_username": "alex-chen-dev"}
            )
            db.add(engineer)
            await db.flush()
            print("  Created employee: engineer.alex@acme.corp (EMPLOYEE - ACTIVE)")

        # New Hire in Onboarding
        nh_stmt = select(Employee).where(Employee.email == "newhire.elena@acme.corp")
        newhire = (await db.execute(nh_stmt)).scalar_one_or_none()
        if not newhire:
            newhire = Employee(
                organization_id=DEMO_ORG_ID,
                email="newhire.elena@acme.corp",
                hashed_password=hashed_pw,
                first_name="Elena",
                last_name="Rostova",
                role=EmployeeRole.EMPLOYEE,
                status=EmploymentStatus.ONBOARDING,
                employment_type=EmploymentType.FULL_TIME,
                department="Engineering",
                job_title="Staff Machine Learning Engineer",
                manager_id=manager.id,
                hire_date=date.today() + timedelta(days=7),
                custom_attributes={"recruiter_candidate_id": "cand_recruiter_9941"}
            )
            db.add(newhire)
            await db.flush()
            print("  Created employee: newhire.elena@acme.corp (EMPLOYEE - ONBOARDING)")

            # Seed onboarding tasks for Elena
            tasks = [
                OnboardingTask(
                    organization_id=DEMO_ORG_ID,
                    employee_id=newhire.id,
                    recruiter_candidate_id="cand_recruiter_9941",
                    title="Submit I-9 and W-4 Tax Documentation",
                    description="Upload government ID and federal withholding forms for compliance verification.",
                    category=OnboardingCategory.DOCUMENTATION,
                    status=OnboardingStatus.COMPLETED,
                    completed_at=datetime.now(timezone.utc),
                    assigned_to_role="EMPLOYEE"
                ),
                OnboardingTask(
                    organization_id=DEMO_ORG_ID,
                    employee_id=newhire.id,
                    recruiter_candidate_id="cand_recruiter_9941",
                    title="Complete Emergency Contacts & Profile Details",
                    description="Fill in emergency contacts, preferred name, and personal communications info.",
                    category=OnboardingCategory.DOCUMENTATION,
                    status=OnboardingStatus.PENDING,
                    due_date=date.today() + timedelta(days=5),
                    assigned_to_role="EMPLOYEE"
                ),
                OnboardingTask(
                    organization_id=DEMO_ORG_ID,
                    employee_id=newhire.id,
                    recruiter_candidate_id="cand_recruiter_9941",
                    title="Provision Corporate Laptop & Hardware Dispatch",
                    description="Configure workstation image, security keys, and arrange courier dispatch.",
                    category=OnboardingCategory.EQUIPMENT,
                    status=OnboardingStatus.IN_PROGRESS,
                    due_date=date.today() + timedelta(days=3),
                    assigned_to_role="IT_ADMIN"
                ),
                OnboardingTask(
                    organization_id=DEMO_ORG_ID,
                    employee_id=newhire.id,
                    recruiter_candidate_id="cand_recruiter_9941",
                    title="Review & Acknowledge Employee Handbook & Code of Conduct",
                    description="Read corporate policies, information security guidelines, and electronically sign acknowledgment.",
                    category=OnboardingCategory.COMPLIANCE,
                    status=OnboardingStatus.PENDING,
                    due_date=date.today() + timedelta(days=7),
                    assigned_to_role="EMPLOYEE"
                )
            ]
            db.add_all(tasks)
            print("  Seeded 4 onboarding tasks for Elena.")

        # 4. Leave Balances for active employees
        current_year = date.today().year
        for emp in [admin, manager, engineer]:
            for pol in created_policies.values():
                b_stmt = select(LeaveBalance).where(
                    LeaveBalance.employee_id == emp.id,
                    LeaveBalance.policy_id == pol.id,
                    LeaveBalance.year == current_year
                )
                existing_bal = (await db.execute(b_stmt)).scalar_one_or_none()
                if not existing_bal:
                    bal = LeaveBalance(
                        employee_id=emp.id,
                        policy_id=pol.id,
                        year=current_year,
                        accrued_days=pol.annual_days_allowed,
                        used_days=2.0 if pol.leave_type == LeaveType.PTO else 0.0,
                        carried_over_days=2.0 if pol.leave_type == LeaveType.PTO else 0.0
                    )
                    db.add(bal)
        print("  Seeded leave balances for active personnel.")

        # 5. Policies with baseline embeddings
        policies_to_seed = [
            (
                "Workplace Flexibility & Remote Work Policy",
                "Workplace Guidelines",
                "Employees are empowered to work remotely or hybrid. Remote employees must maintain core working hours "
                "between 10:00 AM and 4:00 PM in their local time zone. Home office equipment stipends of $1,000 are provided upon joining. "
                "All company-provided equipment must be connected via the corporate VPN."
            ),
            (
                "Paid Time Off (PTO) & Leave Accrual Policy",
                "Leave & Attendance",
                "Full-time employees accrue 1.25 days of Paid Time Off per month, totaling 15 days annually. "
                "Leave requests of 3 or more consecutive days must be submitted at least 2 weeks in advance to allow team calendar scheduling. "
                "A maximum of 5 unused PTO days can be rolled over into the subsequent calendar year; excess days are forfeited."
            ),
            (
                "Information Security & PII Protection Guidelines",
                "Security & Compliance",
                "All corporate data must be handled according to zero-leak standards. Employees are strictly prohibited from entering "
                "unmasked personally identifiable information (PII) including Social Security Numbers, banking details, or customer credentials "
                "into third-party public AI tools. Always use internal platform AI routers which enforce automated PII redaction."
            )
        ]

        # Generate a standard mock 768-dim normalized vector
        mock_vector_768 = [0.035] * 768

        for title, cat, content in policies_to_seed:
            p_stmt = select(PolicyDocument).where(
                PolicyDocument.organization_id == DEMO_ORG_ID,
                PolicyDocument.title == title
            )
            existing_doc = (await db.execute(p_stmt)).scalar_one_or_none()
            if not existing_doc:
                doc = PolicyDocument(
                    organization_id=DEMO_ORG_ID,
                    title=title,
                    category=cat,
                    version="1.0.0",
                    content=content,
                    chunk_index=0,
                    total_chunks=1,
                    embedding_768=mock_vector_768,
                    embedding_model="nomic-embed-text",
                    active_dimension=768,
                    is_active=True,
                    requires_acknowledgment=True
                )
                db.add(doc)
                print(f"  Seeded policy: {title}")

        # 6. Performance Cycle & Goals
        cycle_stmt = select(PerformanceCycle).where(
            PerformanceCycle.organization_id == DEMO_ORG_ID,
            PerformanceCycle.title == "Q4 2026 Engineering Review"
        )
        cycle = (await db.execute(cycle_stmt)).scalar_one_or_none()
        if not cycle:
            cycle = PerformanceCycle(
                organization_id=DEMO_ORG_ID,
                title="Q4 2026 Engineering Review",
                start_date=date(2026, 10, 1),
                end_date=date(2026, 12, 31),
                status=CycleStatus.ACTIVE,
                rubric_config={"dimensions": ["Technical Execution", "Cross-functional Collaboration", "Initiative"]}
            )
            db.add(cycle)
            await db.flush()

            # Seed Goal for Alex Chen
            goal = GoalOKR(
                organization_id=DEMO_ORG_ID,
                cycle_id=cycle.id,
                employee_id=engineer.id,
                title="Deploy pgvector RAG microservice with sub-50ms latency",
                description="Scale policy document indexing and vector cosine retrieval pipeline.",
                key_results={"target_p95_ms": 50, "test_coverage_pct": 90},
                progress_percentage=85.0,
                status=GoalStatus.IN_PROGRESS
            )
            db.add(goal)
            print("  Seeded active performance cycle and engineering goal.")

        await db.commit()
        print("✅ Database seeding completed successfully!")
        print("\nDemo Accounts:")
        print(f"  • HR Admin:       admin@acme.corp           Password: {COMMON_PASSWORD}")
        print(f"  • Manager:        manager.sarah@acme.corp   Password: {COMMON_PASSWORD}")
        print(f"  • Engineer:       engineer.alex@acme.corp   Password: {COMMON_PASSWORD}")
        print(f"  • New Hire:       newhire.elena@acme.corp   Password: {COMMON_PASSWORD}")

if __name__ == "__main__":
    asyncio.run(seed_database())
