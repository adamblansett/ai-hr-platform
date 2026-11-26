import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from backend.app.core.config import settings
from backend.app.schemas.workforce_planning import (
    RecruiterSyncResponse,
    RequisitionForecastCreate,
    RequisitionForecastResponse,
    ScenarioForecastRequest,
    ScenarioForecastResult,
    WorkforcePlanCreate,
    WorkforcePlanResponse,
    WorkforcePlanningSummary,
)

FULLY_LOADED_MULTIPLIER = 1.28

SCENARIO_GROWTH_FACTORS = {
    "CONSERVATIVE": 0.5,
    "BASELINE": 1.0,
    "HYPERGROWTH": 1.5,
}


def compute_fully_loaded_cost(base_salary: float) -> float:
    """Compute employer fully-loaded annual cost (28% taxes, benefits, & equity overhead)."""
    return round(base_salary * FULLY_LOADED_MULTIPLIER, 2)


def simulate_headcount_scenario(
    plan_id: str,
    department: str,
    current_headcount: int,
    target_headcount: int,
    approved_budget_usd: float,
    projected_attrition_rate: float,
    scenario: str,
    avg_base_salary: float,
) -> ScenarioForecastResult:
    factor = SCENARIO_GROWTH_FACTORS.get(scenario, 1.0)
    raw_delta = max(target_headcount - current_headcount, 0)
    net_new_hires = round(raw_delta * factor)
    attrition_backfills = round(current_headcount * projected_attrition_rate)
    total_hiring_need = net_new_hires + attrition_backfills
    projected_end = current_headcount + net_new_hires
    per_hire_loaded = compute_fully_loaded_cost(avg_base_salary)
    estimated_cost = round(total_hiring_need * per_hire_loaded, 2)
    variance = round(approved_budget_usd - estimated_cost, 2)

    if variance < 0:
        recommendation = (
            f"{scenario} scenario exceeds approved {department} budget by "
            f"${abs(variance):,.2f}. Stagger {max(total_hiring_need // 3, 1)} requisitions into Q3/Q4."
        )
    else:
        recommendation = (
            f"{scenario} scenario remains within budget with ${variance:,.2f} headroom. "
            f"Prioritize {attrition_backfills} critical backfill(s) before net-new expansion."
        )

    return ScenarioForecastResult(
        plan_id=plan_id,
        department=department,
        scenario=scenario,
        net_new_hires=net_new_hires,
        attrition_backfills=attrition_backfills,
        total_hiring_need=total_hiring_need,
        projected_headcount_end=projected_end,
        estimated_total_fully_loaded_cost=estimated_cost,
        budget_variance_usd=variance,
        ai_recommendation=recommendation,
    )


class WorkforcePlanningService:
    """AI Workforce Planning, Budget Modeling & ai-recruiter Requisition Sync."""

    def __init__(self):
        self._plans: Dict[str, dict] = {}
        self._requisitions: Dict[str, dict] = {}
        self._seed_defaults()

    def _seed_defaults(self):
        now = datetime.now(timezone.utc)
        p1_id = "wfp-eng-fy2027"
        p2_id = "wfp-sales-fy2027"

        self._plans[p1_id] = {
            "id": p1_id,
            "organization_id": "org-001",
            "fiscal_year": 2027,
            "department": "Engineering",
            "current_headcount": 48,
            "target_headcount": 62,
            "approved_budget_usd": 3800000.0,
            "projected_attrition_rate": 0.08,
            "status": "APPROVED",
            "ai_rationale": "Platform scaling & AI agent roadmap require 14 net-new senior/staff engineers plus 4 attrition backfills.",
            "created_at": now,
            "updated_at": now,
        }
        self._plans[p2_id] = {
            "id": p2_id,
            "organization_id": "org-001",
            "fiscal_year": 2027,
            "department": "Enterprise Sales",
            "current_headcount": 22,
            "target_headcount": 30,
            "approved_budget_usd": 2100000.0,
            "projected_attrition_rate": 0.12,
            "status": "ACTIVE",
            "ai_rationale": "EMEA & North America ARR targets require 8 net-new Enterprise AEs and 3 backfills.",
            "created_at": now,
            "updated_at": now,
        }

        reqs = [
            {
                "id": "req-fc-001",
                "plan_id": p1_id,
                "organization_id": "org-001",
                "role_title": "Staff Distributed Systems Engineer",
                "job_level": "L6",
                "target_quarter": "Q1",
                "estimated_base_salary": 215000.0,
                "fully_loaded_cost": compute_fully_loaded_cost(215000.0),
                "recruiter_sync_status": "SYNCED_TO_RECRUITER",
                "created_at": now,
            },
            {
                "id": "req-fc-002",
                "plan_id": p1_id,
                "organization_id": "org-001",
                "role_title": "Senior Applied AI Engineer",
                "job_level": "L5",
                "target_quarter": "Q2",
                "estimated_base_salary": 190000.0,
                "fully_loaded_cost": compute_fully_loaded_cost(190000.0),
                "recruiter_sync_status": "PENDING",
                "created_at": now,
            },
            {
                "id": "req-fc-003",
                "plan_id": p2_id,
                "organization_id": "org-001",
                "role_title": "Enterprise Account Executive (EMEA)",
                "job_level": "L5",
                "target_quarter": "Q1",
                "estimated_base_salary": 155000.0,
                "fully_loaded_cost": compute_fully_loaded_cost(155000.0),
                "recruiter_sync_status": "PENDING",
                "created_at": now,
            },
        ]
        for r in reqs:
            self._requisitions[r["id"]] = r

    def _hydrate_plan(self, plan: dict) -> WorkforcePlanResponse:
        reqs = [
            RequisitionForecastResponse(**r)
            for r in self._requisitions.values()
            if r["plan_id"] == plan["id"]
        ]
        return WorkforcePlanResponse(**plan, requisitions=reqs)

    def list_plans(self) -> List[WorkforcePlanResponse]:
        return [self._hydrate_plan(p) for p in self._plans.values()]

    def create_plan(self, payload: WorkforcePlanCreate, organization_id: str = "org-001") -> WorkforcePlanResponse:
        now = datetime.now(timezone.utc)
        pid = f"wfp-{uuid.uuid4().hex[:8]}"
        delta = max(payload.target_headcount - payload.current_headcount, 0)
        backfills = round(payload.current_headcount * payload.projected_attrition_rate)
        rationale = (
            f"FY{payload.fiscal_year} {payload.department} plan covers {delta} net-new roles "
            f"and {backfills} projected attrition backfill(s) against ${payload.approved_budget_usd:,.0f} budget."
        )
        record = {
            "id": pid,
            "organization_id": organization_id,
            "fiscal_year": payload.fiscal_year,
            "department": payload.department,
            "current_headcount": payload.current_headcount,
            "target_headcount": payload.target_headcount,
            "approved_budget_usd": payload.approved_budget_usd,
            "projected_attrition_rate": payload.projected_attrition_rate,
            "status": "DRAFT",
            "ai_rationale": rationale,
            "created_at": now,
            "updated_at": now,
        }
        self._plans[pid] = record
        return self._hydrate_plan(record)

    def simulate_plan(self, plan_id: str, payload: ScenarioForecastRequest) -> ScenarioForecastResult:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Workforce plan {plan_id} not found")
        return simulate_headcount_scenario(
            plan_id=plan["id"],
            department=plan["department"],
            current_headcount=plan["current_headcount"],
            target_headcount=plan["target_headcount"],
            approved_budget_usd=plan["approved_budget_usd"],
            projected_attrition_rate=plan["projected_attrition_rate"],
            scenario=payload.scenario,
            avg_base_salary=payload.avg_base_salary,
        )

    def add_requisition(self, plan_id: str, payload: RequisitionForecastCreate) -> RequisitionForecastResponse:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Workforce plan {plan_id} not found")
        rid = f"req-fc-{uuid.uuid4().hex[:8]}"
        record = {
            "id": rid,
            "plan_id": plan_id,
            "organization_id": plan["organization_id"],
            "role_title": payload.role_title,
            "job_level": payload.job_level,
            "target_quarter": payload.target_quarter,
            "estimated_base_salary": payload.estimated_base_salary,
            "fully_loaded_cost": compute_fully_loaded_cost(payload.estimated_base_salary),
            "recruiter_sync_status": "PENDING",
            "created_at": datetime.now(timezone.utc),
        }
        self._requisitions[rid] = record
        return RequisitionForecastResponse(**record)

    def sync_requisition_to_recruiter(self, req_id: str) -> RecruiterSyncResponse:
        req = self._requisitions.get(req_id)
        if not req:
            raise ValueError(f"Requisition forecast {req_id} not found")
        plan = self._plans.get(req["plan_id"], {})
        now = datetime.now(timezone.utc)
        req["recruiter_sync_status"] = "SYNCED_TO_RECRUITER"

        webhook_body = {
            "event": "workforce.requisition_approved",
            "requisition_id": req["id"],
            "organization_id": req["organization_id"],
            "department": plan.get("department", "General"),
            "role_title": req["role_title"],
            "job_level": req["job_level"],
            "target_quarter": req["target_quarter"],
            "salary_band_base_usd": req["estimated_base_salary"],
            "fully_loaded_budget_usd": req["fully_loaded_cost"],
            "timestamp": now.isoformat(),
        }
        serialized = json.dumps(webhook_body, sort_keys=True).encode("utf-8")
        signature = hmac.new(
            settings.RECRUITER_WEBHOOK_SECRET.encode("utf-8"),
            serialized,
            hashlib.sha256,
        ).hexdigest()

        return RecruiterSyncResponse(
            requisition_id=req["id"],
            recruiter_sync_status="SYNCED_TO_RECRUITER",
            webhook_event="workforce.requisition_approved",
            signed_payload={**webhook_body, "hmac_sha256": f"sha256={signature}"},
            synced_at=now,
        )

    def get_summary(self) -> WorkforcePlanningSummary:
        plans = list(self._plans.values())
        reqs = list(self._requisitions.values())
        return WorkforcePlanningSummary(
            total_plans=len(plans),
            total_current_headcount=sum(p["current_headcount"] for p in plans),
            total_target_headcount=sum(p["target_headcount"] for p in plans),
            total_approved_budget_usd=round(sum(p["approved_budget_usd"] for p in plans), 2),
            total_open_requisitions=len(reqs),
            synced_to_recruiter_count=sum(
                1 for r in reqs if r["recruiter_sync_status"] == "SYNCED_TO_RECRUITER"
            ),
        )


workforce_planning_service = WorkforcePlanningService()
