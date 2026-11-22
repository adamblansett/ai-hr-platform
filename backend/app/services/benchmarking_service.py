import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.benchmarking import (
    SalaryBenchmarkCreate,
    SalaryBenchmarkResponse,
    EmployeeCompensationAudit,
    DepartmentBenchmarkingSummary,
)


class BenchmarkingService:
    def __init__(self):
        self._benchmarks: Dict[str, dict] = {}
        self._seed_default_benchmarks()

    def _seed_default_benchmarks(self):
        b1 = {
            "id": "bm-eng-l5-bay",
            "job_title": "Senior Software Engineer",
            "department": "Engineering",
            "job_level": "L5",
            "geo_zone": "US_BAY_AREA",
            "base_salary_p25": 165000.0,
            "base_salary_p50": 185000.0,
            "base_salary_p75": 210000.0,
            "base_salary_p90": 235000.0,
            "equity_shares_p50": 18000.0,
            "variable_bonus_target_pct": 15.0,
            "currency": "USD",
            "updated_at": datetime(2026, 10, 1, 9, 0, 0),
        }
        b2 = {
            "id": "bm-eng-l6-bay",
            "job_title": "Staff Software Engineer",
            "department": "Engineering",
            "job_level": "L6",
            "geo_zone": "US_BAY_AREA",
            "base_salary_p25": 215000.0,
            "base_salary_p50": 240000.0,
            "base_salary_p75": 270000.0,
            "base_salary_p90": 305000.0,
            "equity_shares_p50": 32000.0,
            "variable_bonus_target_pct": 20.0,
            "currency": "USD",
            "updated_at": datetime(2026, 10, 1, 9, 0, 0),
        }
        b3 = {
            "id": "bm-devops-l5-remote",
            "job_title": "Senior Site Reliability Engineer",
            "department": "DevOps",
            "job_level": "L5",
            "geo_zone": "US_REMOTE",
            "base_salary_p25": 145000.0,
            "base_salary_p50": 165000.0,
            "base_salary_p75": 185000.0,
            "base_salary_p90": 205000.0,
            "equity_shares_p50": 14000.0,
            "variable_bonus_target_pct": 15.0,
            "currency": "USD",
            "updated_at": datetime(2026, 10, 1, 9, 0, 0),
        }
        self._benchmarks[b1["id"]] = b1
        self._benchmarks[b2["id"]] = b2
        self._benchmarks[b3["id"]] = b3

    def list_benchmarks(
        self,
        department: Optional[str] = None,
        job_level: Optional[str] = None,
    ) -> List[SalaryBenchmarkResponse]:
        results = list(self._benchmarks.values())
        if department:
            results = [b for b in results if b["department"].lower() == department.lower()]
        if job_level:
            results = [b for b in results if b["job_level"].upper() == job_level.upper()]
        return [SalaryBenchmarkResponse(**b) for b in results]

    def create_benchmark(self, payload: SalaryBenchmarkCreate) -> SalaryBenchmarkResponse:
        bm_id = f"bm-{uuid.uuid4().hex[:8]}"
        record = {
            "id": bm_id,
            "job_title": payload.job_title,
            "department": payload.department,
            "job_level": payload.job_level,
            "geo_zone": payload.geo_zone,
            "base_salary_p25": payload.base_salary_p25,
            "base_salary_p50": payload.base_salary_p50,
            "base_salary_p75": payload.base_salary_p75,
            "base_salary_p90": payload.base_salary_p90,
            "equity_shares_p50": payload.equity_shares_p50,
            "variable_bonus_target_pct": payload.variable_bonus_target_pct,
            "currency": payload.currency,
            "updated_at": datetime.utcnow(),
        }
        self._benchmarks[bm_id] = record
        return SalaryBenchmarkResponse(**record)

    def audit_department_compensation(self, department: str = "Engineering") -> DepartmentBenchmarkingSummary:
        # Mock active employees in department
        employees = [
            {
                "id": "emp-001",
                "name": "Alex Chen",
                "job_title": "Senior Software Engineer",
                "department": "Engineering",
                "job_level": "L5",
                "geo_zone": "US_BAY_AREA",
                "current_base_salary": 178000.0,
            },
            {
                "id": "emp-002",
                "name": "Sarah Miller",
                "job_title": "Staff Software Engineer",
                "department": "Engineering",
                "job_level": "L6",
                "geo_zone": "US_BAY_AREA",
                "current_base_salary": 245000.0,
            },
            {
                "id": "emp-004",
                "name": "Elena Rostova",
                "job_title": "Senior Software Engineer",
                "department": "Engineering",
                "job_level": "L5",
                "geo_zone": "US_BAY_AREA",
                "current_base_salary": 160000.0,  # Below P50
            },
        ]

        audits: List[EmployeeCompensationAudit] = []
        total_gap = 0.0
        below_p50_count = 0

        for emp in employees:
            # Find matching benchmark
            bm = next(
                (b for b in self._benchmarks.values() if b["job_level"] == emp["job_level"] and b["department"] == emp["department"]),
                list(self._benchmarks.values())[0],
            )
            p50 = bm["base_salary_p50"]
            current = emp["current_base_salary"]
            ratio = round(current / p50, 3)

            if ratio < 0.85:
                pos = "BELOW_RANGE"
                risk = "HIGH"
                adj = p50 - current
            elif ratio < 0.95:
                pos = "LOWER_QUARTILE"
                risk = "MODERATE"
                adj = p50 - current
            elif ratio <= 1.05:
                pos = "AT_MARKET"
                risk = "LOW"
                adj = 0.0
            elif ratio <= 1.15:
                pos = "UPPER_QUARTILE"
                risk = "LOW"
                adj = 0.0
            else:
                pos = "ABOVE_RANGE"
                risk = "LOW"
                adj = 0.0

            if adj > 0:
                below_p50_count += 1
                total_gap += adj

            audits.append(
                EmployeeCompensationAudit(
                    employee_id=emp["id"],
                    employee_name=emp["name"],
                    job_title=emp["job_title"],
                    department=emp["department"],
                    job_level=emp["job_level"],
                    geo_zone=emp["geo_zone"],
                    current_base_salary=current,
                    market_p50=p50,
                    compa_ratio=ratio,
                    band_position=pos,
                    suggested_merit_adjustment=round(adj, 2),
                    retention_risk_level=risk,
                )
            )

        avg_ratio = round(sum(a.compa_ratio for a in audits) / len(audits), 3) if audits else 1.0

        return DepartmentBenchmarkingSummary(
            department=department,
            average_compa_ratio=avg_ratio,
            employees_below_p50_count=below_p50_count,
            total_budget_gap_to_p50=round(total_gap, 2),
            audits=audits,
        )


benchmarking_service = BenchmarkingService()
