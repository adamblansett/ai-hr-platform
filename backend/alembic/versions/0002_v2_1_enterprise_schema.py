"""Enterprise schema v2.0 + v2.1 (Comp, Succession, Webhooks, Lifecycle, Ops, Global & Security)

Revision ID: 0002_v2_1_enterprise_schema
Revises: 0001_initial_schema
Create Date: 2026-11-26 07:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_v2_1_enterprise_schema"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Compensation, Equity & Payroll
    op.create_table(
        "compensation_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("base_salary", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("pay_frequency", sa.Enum("WEEKLY", "BI_WEEKLY", "SEMI_MONTHLY", "MONTHLY", name="payfrequency"), nullable=False),
        sa.Column("target_bonus_percentage", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_compensation_packages_organization_id", "compensation_packages", ["organization_id"])
    op.create_index("ix_compensation_packages_employee_id", "compensation_packages", ["employee_id"])

    op.create_table(
        "equity_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grant_number", sa.String(length=50), nullable=False),
        sa.Column("grant_type", sa.Enum("RSU", "ISO", "NSO", "SAR", name="equitygranttype"), nullable=False),
        sa.Column("total_shares", sa.Integer(), nullable=False),
        sa.Column("strike_price", sa.Float(), nullable=False),
        sa.Column("grant_date", sa.Date(), nullable=False),
        sa.Column("vesting_start_date", sa.Date(), nullable=False),
        sa.Column("cliff_months", sa.Integer(), nullable=False),
        sa.Column("vesting_duration_months", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_equity_grants_organization_id", "equity_grants", ["organization_id"])
    op.create_index("ix_equity_grants_employee_id", "equity_grants", ["employee_id"])
    op.create_index("ix_equity_grants_grant_number", "equity_grants", ["grant_number"], unique=True)

    op.create_table(
        "paystub_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pay_period_start", sa.Date(), nullable=False),
        sa.Column("pay_period_end", sa.Date(), nullable=False),
        sa.Column("pay_date", sa.Date(), nullable=False),
        sa.Column("gross_amount", sa.Float(), nullable=False),
        sa.Column("net_amount", sa.Float(), nullable=False),
        sa.Column("tax_withholdings", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("benefit_deductions", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("pdf_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_paystub_records_organization_id", "paystub_records", ["organization_id"])
    op.create_index("ix_paystub_records_employee_id", "paystub_records", ["employee_id"])

    # 2. Succession & Career Mobility
    op.create_table(
        "skill_competencies",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("proficiency_level", sa.Integer(), nullable=True),
        sa.Column("verified_by_manager", sa.Boolean(), nullable=True),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_skill_competencies_organization_id", "skill_competencies", ["organization_id"])
    op.create_index("ix_skill_competencies_employee_id", "skill_competencies", ["employee_id"])
    op.create_index("ix_skill_competencies_skill_name", "skill_competencies", ["skill_name"])

    op.create_table(
        "flight_risk_assessments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("contributing_factors", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("recommended_interventions", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_flight_risk_assessments_organization_id", "flight_risk_assessments", ["organization_id"])
    op.create_index("ix_flight_risk_assessments_employee_id", "flight_risk_assessments", ["employee_id"])

    op.create_table(
        "internal_requisitions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("min_experience_years", sa.Integer(), nullable=True),
        sa.Column("required_skills", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("target_headcount", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_internal_requisitions_organization_id", "internal_requisitions", ["organization_id"])

    # 3. Outbound Webhooks
    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_url", sa.String(length=500), nullable=False),
        sa.Column("secret_key", sa.String(length=128), nullable=False),
        sa.Column("event_types", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_webhook_subscriptions_organization_id", "webhook_subscriptions", ["organization_id"])

    op.create_table(
        "webhook_delivery_logs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("subscription_id", sa.String(length=36), sa.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_webhook_delivery_logs_subscription_id", "webhook_delivery_logs", ["subscription_id"])

    # 4. Offboarding & Exit Interviews
    op.create_table(
        "offboarding_records",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("initiator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_working_day", sa.Date(), nullable=False),
        sa.Column("termination_reason", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("scim_deprovisioned", sa.Boolean(), nullable=True),
        sa.Column("equipment_returned", sa.Boolean(), nullable=True),
        sa.Column("nda_reaffirmed", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_offboarding_records_organization_id", "offboarding_records", ["organization_id"])
    op.create_index("ix_offboarding_records_employee_id", "offboarding_records", ["employee_id"])

    op.create_table(
        "offboarding_tasks",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("offboarding_id", sa.String(length=36), sa.ForeignKey("offboarding_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_offboarding_tasks_offboarding_id", "offboarding_tasks", ["offboarding_id"])

    op.create_table(
        "exit_interview_feedbacks",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("offboarding_id", sa.String(length=36), sa.ForeignKey("offboarding_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("primary_reason", sa.String(length=100), nullable=False),
        sa.Column("experience_rating", sa.Integer(), nullable=True),
        sa.Column("manager_feedback", sa.Text(), nullable=True),
        sa.Column("company_culture_feedback", sa.Text(), nullable=True),
        sa.Column("ai_synthesized_insights", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_exit_interview_feedbacks_offboarding_id", "exit_interview_feedbacks", ["offboarding_id"])
    op.create_index("ix_exit_interview_feedbacks_employee_id", "exit_interview_feedbacks", ["employee_id"])

    # 5. Coaching & Calibration
    op.create_table(
        "one_on_one_meetings",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("talking_points", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("ai_suggested_prompts", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("manager_notes", sa.Text(), nullable=True),
        sa.Column("action_items", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_one_on_one_meetings_organization_id", "one_on_one_meetings", ["organization_id"])
    op.create_index("ix_one_on_one_meetings_manager_id", "one_on_one_meetings", ["manager_id"])
    op.create_index("ix_one_on_one_meetings_employee_id", "one_on_one_meetings", ["employee_id"])

    op.create_table(
        "calibration_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cycle_name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("total_reviewed", sa.Integer(), nullable=True),
        sa.Column("rating_distribution", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("detected_biases", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("recommendations", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_calibration_sessions_organization_id", "calibration_sessions", ["organization_id"])

    # 6. Pulse & Sentiment
    op.create_table(
        "pulse_surveys",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_pulse_surveys_organization_id", "pulse_surveys", ["organization_id"])

    op.create_table(
        "pulse_responses",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("survey_id", sa.String(length=36), sa.ForeignKey("pulse_surveys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("respondent_hash", sa.String(length=64), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_pulse_responses_survey_id", "pulse_responses", ["survey_id"])
    op.create_index("ix_pulse_responses_organization_id", "pulse_responses", ["organization_id"])
    op.create_index("ix_pulse_responses_respondent_hash", "pulse_responses", ["respondent_hash"])

    op.create_table(
        "department_sentiment_scores",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("enps_score", sa.Float(), nullable=True),
        sa.Column("avg_rating", sa.Float(), nullable=True),
        sa.Column("burnout_risk_level", sa.String(length=20), nullable=True),
        sa.Column("total_responses", sa.Integer(), nullable=True),
        sa.Column("ai_action_recommendations", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_department_sentiment_scores_organization_id", "department_sentiment_scores", ["organization_id"])

    # 7. Benefits Administration
    op.create_table(
        "benefit_plans",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_name", sa.String(length=150), nullable=False),
        sa.Column("plan_type", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("tier_name", sa.String(length=50), nullable=True),
        sa.Column("monthly_employee_premium", sa.Float(), nullable=True),
        sa.Column("monthly_employer_contribution", sa.Float(), nullable=True),
        sa.Column("annual_deductible", sa.Float(), nullable=True),
        sa.Column("out_of_pocket_max", sa.Float(), nullable=True),
        sa.Column("summary_of_benefits", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_benefit_plans_organization_id", "benefit_plans", ["organization_id"])

    op.create_table(
        "employee_benefit_elections",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.String(length=36), sa.ForeignKey("benefit_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("coverage_tier", sa.String(length=50), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("employee_monthly_cost", sa.Float(), nullable=False),
        sa.Column("employer_monthly_cost", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_employee_benefit_elections_organization_id", "employee_benefit_elections", ["organization_id"])
    op.create_index("ix_employee_benefit_elections_employee_id", "employee_benefit_elections", ["employee_id"])
    op.create_index("ix_employee_benefit_elections_plan_id", "employee_benefit_elections", ["plan_id"])

    # 8. Time & Attendance
    op.create_table(
        "timesheet_entries",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shift_date", sa.Date(), nullable=False),
        sa.Column("clock_in", sa.DateTime(timezone=True), nullable=False),
        sa.Column("clock_out", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_hours", sa.Float(), nullable=True),
        sa.Column("regular_hours", sa.Float(), nullable=True),
        sa.Column("overtime_hours", sa.Float(), nullable=True),
        sa.Column("double_time_hours", sa.Float(), nullable=True),
        sa.Column("meal_break_minutes", sa.Integer(), nullable=True),
        sa.Column("meal_penalty_flag", sa.Boolean(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_timesheet_entries_organization_id", "timesheet_entries", ["organization_id"])
    op.create_index("ix_timesheet_entries_employee_id", "timesheet_entries", ["employee_id"])

    # 9. Expense Reports & Items
    op.create_table(
        "expense_reports",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("audit_status", sa.String(length=30), nullable=False),
        sa.Column("audit_notes", sa.Text(), nullable=True),
        sa.Column("reimbursement_reference", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "expense_items",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("report_id", sa.String(length=36), sa.ForeignKey("expense_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("expense_date", sa.String(length=10), nullable=False),
        sa.Column("merchant", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("receipt_url", sa.String(length=255), nullable=True),
        sa.Column("is_compliant", sa.Boolean(), nullable=False),
        sa.Column("policy_flags", sa.Text(), nullable=True),
    )

    # 10. Workplace Health & Safety
    op.create_table(
        "safety_incidents",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("incident_type", sa.String(length=30), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("incident_date", sa.String(length=10), nullable=False),
        sa.Column("location", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_osha_recordable", sa.Boolean(), nullable=False),
        sa.Column("osha_case_number", sa.String(length=50), nullable=True),
        sa.Column("lost_workday_count", sa.Integer(), nullable=False),
        sa.Column("restricted_days_count", sa.Integer(), nullable=False),
        sa.Column("ai_root_cause_analysis", sa.Text(), nullable=True),
        sa.Column("corrective_actions", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # 11. Peer Recognition & Rewards
    op.create_table(
        "peer_recognitions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("core_value", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "reward_catalog_items",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("points_cost", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("image_url", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "employee_recognition_wallets",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("points_balance", sa.Integer(), nullable=False),
        sa.Column("monthly_allowance_remaining", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # 12. Learning & Development / LMS
    op.create_table(
        "learning_courses",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False),
        sa.Column("passing_score_percentage", sa.Integer(), nullable=False),
        sa.Column("certification_validity_days", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "course_enrollments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.String(length=36), sa.ForeignKey("learning_courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("certificate_id", sa.String(length=50), nullable=True),
    )

    # 13. Hardware Asset Fleet
    op.create_table(
        "hardware_assets",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("asset_tag", sa.String(length=50), nullable=False, unique=True),
        sa.Column("serial_number", sa.String(length=100), nullable=False, unique=True),
        sa.Column("device_model", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=True),
        sa.Column("purchase_date", sa.String(length=10), nullable=False),
        sa.Column("warranty_expiry", sa.String(length=10), nullable=False),
        sa.Column("device_condition", sa.String(length=30), nullable=False),
        sa.Column("mdm_enrolled", sa.Boolean(), nullable=False),
        sa.Column("mdm_provider", sa.String(length=30), nullable=False),
        sa.Column("mdm_device_id", sa.String(length=100), nullable=True),
        sa.Column("mdm_last_checkin", sa.DateTime(), nullable=True),
        sa.Column("remote_wipe_status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # 14. Global Contractor & EOR Hub
    op.create_table(
        "contractor_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False, unique=True),
        sa.Column("country", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("tax_form_type", sa.String(length=30), nullable=False),
        sa.Column("tax_form_verified", sa.Boolean(), nullable=False),
        sa.Column("tax_id_masked", sa.String(length=50), nullable=True),
        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "contractor_sows",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("contractor_id", sa.String(length=36), sa.ForeignKey("contractor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("total_budget", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("start_date", sa.String(length=10), nullable=False),
        sa.Column("end_date", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("deliverables_description", sa.Text(), nullable=True),
    )

    op.create_table(
        "milestone_invoices",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sow_id", sa.String(length=36), sa.ForeignKey("contractor_sows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contractor_id", sa.String(length=36), sa.ForeignKey("contractor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("milestone_title", sa.String(length=200), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("payout_tx_hash", sa.String(length=100), nullable=True),
    )

    # 15. Salary Benchmarking
    op.create_table(
        "salary_benchmarks",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("job_title", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=50), nullable=False),
        sa.Column("job_level", sa.String(length=10), nullable=False),
        sa.Column("geo_zone", sa.String(length=30), nullable=False),
        sa.Column("base_salary_p25", sa.Float(), nullable=False),
        sa.Column("base_salary_p50", sa.Float(), nullable=False),
        sa.Column("base_salary_p75", sa.Float(), nullable=False),
        sa.Column("base_salary_p90", sa.Float(), nullable=False),
        sa.Column("equity_shares_p50", sa.Float(), nullable=False),
        sa.Column("variable_bonus_target_pct", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # 16. Immigration & Global Relocation
    op.create_table(
        "immigration_cases",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("visa_type", sa.String(length=30), nullable=False),
        sa.Column("case_status", sa.String(length=30), nullable=False),
        sa.Column("uscis_receipt_number", sa.String(length=50), nullable=True),
        sa.Column("uscis_center", sa.String(length=50), nullable=True),
        sa.Column("filing_date", sa.String(length=10), nullable=True),
        sa.Column("expiry_date", sa.String(length=10), nullable=False),
        sa.Column("assigned_attorney", sa.String(length=100), nullable=False),
        sa.Column("relocation_stipend_amount", sa.Float(), nullable=False),
        sa.Column("stipend_disbursed", sa.Boolean(), nullable=False),
        sa.Column("tax_gross_up_amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "immigration_documents",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("immigration_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("document_name", sa.String(length=150), nullable=False),
        sa.Column("document_url", sa.String(length=255), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
    )

    # 17. Multi-Tenant Branding
    op.create_table(
        "tenant_branding_configs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False, unique=True),
        sa.Column("company_name", sa.String(length=100), nullable=False),
        sa.Column("custom_domain", sa.String(length=150), nullable=False),
        sa.Column("custom_domain_verified", sa.Boolean(), nullable=False),
        sa.Column("ssl_cert_status", sa.String(length=30), nullable=False),
        sa.Column("primary_color_hex", sa.String(length=10), nullable=False),
        sa.Column("secondary_color_hex", sa.String(length=10), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=False),
        sa.Column("favicon_url", sa.String(length=255), nullable=False),
        sa.Column("support_email", sa.String(length=100), nullable=False),
        sa.Column("portal_title", sa.String(length=100), nullable=False),
        sa.Column("kms_key_id", sa.String(length=100), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # 18. Enterprise SSO & MFA (v2.1.0)
    op.create_table(
        "sso_provider_configs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_type", sa.String(length=20), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("issuer_url", sa.String(length=500), nullable=False),
        sa.Column("sso_login_url", sa.String(length=500), nullable=False),
        sa.Column("client_id", sa.String(length=255), nullable=True),
        sa.Column("certificate_fingerprint", sa.String(length=255), nullable=True),
        sa.Column("enforced_for_admins", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sso_provider_configs_organization_id", "sso_provider_configs", ["organization_id"])

    op.create_table(
        "user_mfa_settings",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("totp_secret", sa.String(length=128), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("backup_codes_hashed", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_mfa_settings_organization_id", "user_mfa_settings", ["organization_id"])

    # 19. Event-Driven Notifications & Digests (v2.1.0)
    op.create_table(
        "notification_dispatches",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("metadata_json", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notification_dispatches_organization_id", "notification_dispatches", ["organization_id"])
    op.create_index("ix_notification_dispatches_recipient_employee_id", "notification_dispatches", ["recipient_employee_id"])

    # 20. AI Workforce Planning & Headcount Forecasting (v2.1.0)
    op.create_table(
        "workforce_plans",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("current_headcount", sa.Integer(), nullable=False),
        sa.Column("target_headcount", sa.Integer(), nullable=False),
        sa.Column("approved_budget_usd", sa.Float(), nullable=False),
        sa.Column("projected_attrition_rate", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("ai_rationale", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workforce_plans_organization_id", "workforce_plans", ["organization_id"])

    op.create_table(
        "headcount_requisition_forecasts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("plan_id", sa.String(length=36), sa.ForeignKey("workforce_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_title", sa.String(length=150), nullable=False),
        sa.Column("job_level", sa.String(length=30), nullable=False),
        sa.Column("target_quarter", sa.String(length=10), nullable=False),
        sa.Column("estimated_base_salary", sa.Float(), nullable=False),
        sa.Column("fully_loaded_cost", sa.Float(), nullable=False),
        sa.Column("recruiter_sync_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_headcount_requisition_forecasts_plan_id", "headcount_requisition_forecasts", ["plan_id"])
    op.create_index("ix_headcount_requisition_forecasts_organization_id", "headcount_requisition_forecasts", ["organization_id"])


def downgrade() -> None:
    op.drop_table("headcount_requisition_forecasts")
    op.drop_table("workforce_plans")
    op.drop_table("notification_dispatches")
    op.drop_table("user_mfa_settings")
    op.drop_table("sso_provider_configs")
    op.drop_table("tenant_branding_configs")
    op.drop_table("immigration_documents")
    op.drop_table("immigration_cases")
    op.drop_table("salary_benchmarks")
    op.drop_table("milestone_invoices")
    op.drop_table("contractor_sows")
    op.drop_table("contractor_profiles")
    op.drop_table("hardware_assets")
    op.drop_table("course_enrollments")
    op.drop_table("learning_courses")
    op.drop_table("employee_recognition_wallets")
    op.drop_table("reward_catalog_items")
    op.drop_table("peer_recognitions")
    op.drop_table("safety_incidents")
    op.drop_table("expense_items")
    op.drop_table("expense_reports")
    op.drop_table("timesheet_entries")
    op.drop_table("employee_benefit_elections")
    op.drop_table("benefit_plans")
    op.drop_table("department_sentiment_scores")
    op.drop_table("pulse_responses")
    op.drop_table("pulse_surveys")
    op.drop_table("calibration_sessions")
    op.drop_table("one_on_one_meetings")
    op.drop_table("exit_interview_feedbacks")
    op.drop_table("offboarding_tasks")
    op.drop_table("offboarding_records")
    op.drop_table("webhook_delivery_logs")
    op.drop_table("webhook_subscriptions")
    op.drop_table("internal_requisitions")
    op.drop_table("flight_risk_assessments")
    op.drop_table("skill_competencies")
    op.drop_table("paystub_records")
    op.drop_table("equity_grants")
    op.drop_table("compensation_packages")

    op.execute("DROP TYPE IF EXISTS equitygranttype;")
    op.execute("DROP TYPE IF EXISTS payfrequency;")
