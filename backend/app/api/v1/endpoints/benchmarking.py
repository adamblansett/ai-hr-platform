from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.benchmarking import (
    SalaryBenchmarkCreate,
    SalaryBenchmarkResponse,
    DepartmentBenchmarkingSummary,
)
from backend.app.services.benchmarking_service import benchmarking_service

router = APIRouter()


@router.get("/", response_model=List[SalaryBenchmarkResponse])
def list_salary_benchmarks(
    department: Optional[str] = Query(None),
    job_level: Optional[str] = Query(None),
):
    """Retrieve market compensation benchmarks across percentiles (P25, P50, P75, P90)."""
    return benchmarking_service.list_benchmarks(department=department, job_level=job_level)


@router.post("/", response_model=SalaryBenchmarkResponse, status_code=status.HTTP_201_CREATED)
def create_salary_benchmark(payload: SalaryBenchmarkCreate):
    """Record a new compensation benchmark from market salary surveys."""
    return benchmarking_service.create_benchmark(payload)


@router.get("/audit/department", response_model=DepartmentBenchmarkingSummary)
def audit_department_compensation(department: str = Query("Engineering")):
    """Run an automated compa-ratio audit and calculate budget gap to market P50 median."""
    return benchmarking_service.audit_department_compensation(department=department)
