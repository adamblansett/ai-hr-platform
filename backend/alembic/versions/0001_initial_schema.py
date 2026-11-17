"""Initial schema with multi-tenancy, pgvector, and core HR models

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-17 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Table: organizations
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("settings", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_organizations_slug"), "organizations", ["slug"], unique=True)
    op.create_index(op.f("ix_organizations_domain"), "organizations", ["domain"], unique=True)

    # 3. Table: employees
    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("preferred_name", sa.String(length=100), nullable=True),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("role", sa.Enum("SUPER_ADMIN", "HR_ADMIN", "PEOPLE_MANAGER", "EMPLOYEE", name="employeerole"), nullable=False),
        sa.Column("status", sa.Enum("ONBOARDING", "ACTIVE", "ON_LEAVE", "TERMINATED", name="employmentstatus"), nullable=False),
        sa.Column("employment_type", sa.Enum("FULL_TIME", "PART_TIME", "CONTRACTOR", "INTERN", name="employmenttype"), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("job_title", sa.String(length=150), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("termination_date", sa.Date(), nullable=True),
        sa.Column("custom_attributes", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_employees_organization_id"), "employees", ["organization_id"], unique=False)
    op.create_index(op.f("ix_employees_email"), "employees", ["email"], unique=True)
    op.create_index(op.f("ix_employees_status"), "employees", ["status"], unique=False)
    op.create_index(op.f("ix_employees_department"), "employees", ["department"], unique=False)
    op.create_index(op.f("ix_employees_manager_id"), "employees", ["manager_id"], unique=False)

    # 4. Table: onboarding_tasks
    op.create_table(
        "onboarding_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recruiter_candidate_id", sa.String(length=100), nullable=True),
        sa.Column("offer_acceptance_reference", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.Enum("DOCUMENTATION", "EQUIPMENT", "ACCESS_PROVISIONING", "TRAINING", "COMPLIANCE", name="onboardingcategory"), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "BLOCKED", "WAIVED", name="onboardingstatus"), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to_role", sa.String(length=50), nullable=False),
        sa.Column("document_url", sa.String(length=500), nullable=True),
        sa.Column("external_system_payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_onboarding_tasks_organization_id"), "onboarding_tasks", ["organization_id"], unique=False)
    op.create_index(op.f("ix_onboarding_tasks_employee_id"), "onboarding_tasks", ["employee_id"], unique=False)
    op.create_index(op.f("ix_onboarding_tasks_recruiter_candidate_id"), "onboarding_tasks", ["recruiter_candidate_id"], unique=False)
    op.create_index(op.f("ix_onboarding_tasks_status"), "onboarding_tasks", ["status"], unique=False)

    # 5. Table: policy_documents
    op.create_table(
        "policy_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False, default=0),
        sa.Column("total_chunks", sa.Integer(), nullable=False, default=1),
        sa.Column("embedding_768", Vector(768), nullable=True),
        sa.Column("embedding_1536", Vector(1536), nullable=True),
        sa.Column("embedding_model", sa.String(length=100), nullable=True),
        sa.Column("active_dimension", sa.Integer(), nullable=False, default=768),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("requires_acknowledgment", sa.Boolean(), nullable=False, default=False),
        sa.Column("source_file_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_policy_documents_organization_id"), "policy_documents", ["organization_id"], unique=False)
    op.create_index(op.f("ix_policy_documents_category"), "policy_documents", ["category"], unique=False)

    # 6. Table: policy_acknowledgments
    op.create_table(
        "policy_acknowledgments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signature_hash", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_policy_acknowledgments_policy_id"), "policy_acknowledgments", ["policy_id"], unique=False)
    op.create_index(op.f("ix_policy_acknowledgments_employee_id"), "policy_acknowledgments", ["employee_id"], unique=False)

    # 7. Table: leave_policies
    op.create_table(
        "leave_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("leave_type", sa.Enum("PTO", "SICK", "PARENTAL", "BEREAVEMENT", "UNPAID", name="leavetype"), nullable=False),
        sa.Column("annual_days_allowed", sa.Float(), nullable=False, default=15.0),
        sa.Column("accrual_rate_per_month", sa.Float(), nullable=False, default=1.25),
        sa.Column("max_carryover_days", sa.Float(), nullable=False, default=5.0),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_leave_policies_organization_id"), "leave_policies", ["organization_id"], unique=False)

    # 8. Table: leave_balances
    op.create_table(
        "leave_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leave_policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("accrued_days", sa.Float(), nullable=False, default=0.0),
        sa.Column("used_days", sa.Float(), nullable=False, default=0.0),
        sa.Column("carried_over_days", sa.Float(), nullable=False, default=0.0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_leave_balances_employee_id"), "leave_balances", ["employee_id"], unique=False)
    op.create_index(op.f("ix_leave_balances_policy_id"), "leave_balances", ["policy_id"], unique=False)

    # 9. Table: leave_requests
    op.create_table(
        "leave_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leave_policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "APPROVED", "REJECTED", "CANCELLED", name="leavestatus"), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("calendar_conflict_flag", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_leave_requests_organization_id"), "leave_requests", ["organization_id"], unique=False)
    op.create_index(op.f("ix_leave_requests_employee_id"), "leave_requests", ["employee_id"], unique=False)
    op.create_index(op.f("ix_leave_requests_status"), "leave_requests", ["status"], unique=False)

    # 10. Table: performance_cycles
    op.create_table(
        "performance_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.Enum("UPCOMING", "ACTIVE", "EVALUATION", "CLOSED", name="cyclestatus"), nullable=False),
        sa.Column("rubric_config", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_performance_cycles_organization_id"), "performance_cycles", ["organization_id"], unique=False)
    op.create_index(op.f("ix_performance_cycles_status"), "performance_cycles", ["status"], unique=False)

    # 11. Table: goal_okrs
    op.create_table(
        "goal_okrs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("performance_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("key_results", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("progress_percentage", sa.Float(), nullable=False, default=0.0),
        sa.Column("status", sa.Enum("NOT_STARTED", "IN_PROGRESS", "ACHIEVED", "EXCEEDED", "MISSED", name="goalstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_goal_okrs_organization_id"), "goal_okrs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_goal_okrs_cycle_id"), "goal_okrs", ["cycle_id"], unique=False)
    op.create_index(op.f("ix_goal_okrs_employee_id"), "goal_okrs", ["employee_id"], unique=False)

    # 12. Table: review_feedbacks
    op.create_table(
        "review_feedbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("performance_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship", sa.Enum("SELF", "MANAGER", "PEER", "DIRECT_REPORT", name="reviewrelationship"), nullable=False),
        sa.Column("ratings", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("qualitative_feedback", sa.Text(), nullable=False, default=""),
        sa.Column("ai_synthesized_summary", sa.Text(), nullable=True),
        sa.Column("is_submitted", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_review_feedbacks_organization_id"), "review_feedbacks", ["organization_id"], unique=False)
    op.create_index(op.f("ix_review_feedbacks_cycle_id"), "review_feedbacks", ["cycle_id"], unique=False)
    op.create_index(op.f("ix_review_feedbacks_reviewee_id"), "review_feedbacks", ["reviewee_id"], unique=False)
    op.create_index(op.f("ix_review_feedbacks_reviewer_id"), "review_feedbacks", ["reviewer_id"], unique=False)

    # 13. Table: audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("pii_redacted", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_audit_logs_organization_id"), "audit_logs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("review_feedbacks")
    op.drop_table("goal_okrs")
    op.drop_table("performance_cycles")
    op.drop_table("leave_requests")
    op.drop_table("leave_balances")
    op.drop_table("leave_policies")
    op.drop_table("policy_acknowledgments")
    op.drop_table("policy_documents")
    op.drop_table("onboarding_tasks")
    op.drop_table("employees")
    op.drop_table("organizations")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS reviewrelationship;")
    op.execute("DROP TYPE IF EXISTS goalstatus;")
    op.execute("DROP TYPE IF EXISTS cyclestatus;")
    op.execute("DROP TYPE IF EXISTS leavestatus;")
    op.execute("DROP TYPE IF EXISTS leavetype;")
    op.execute("DROP TYPE IF EXISTS onboardingstatus;")
    op.execute("DROP TYPE IF EXISTS onboardingcategory;")
    op.execute("DROP TYPE IF EXISTS employmenttype;")
    op.execute("DROP TYPE IF EXISTS employmentstatus;")
    op.execute("DROP TYPE IF EXISTS employeerole;")

    op.execute("DROP EXTENSION IF EXISTS vector;")
