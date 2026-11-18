import uuid
from typing import Dict, Any, List
from collections import defaultdict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.employee import Employee, EmploymentStatus
from backend.app.models.onboarding import OnboardingTask, OnboardingStatus
from backend.app.models.leave import LeaveRequest, LeavePolicy, LeaveStatus
from backend.app.models.performance import PerformanceCycle, GoalOKR, ReviewFeedback, CycleStatus
from backend.app.schemas.analytics import (
    HROverviewMetrics,
    LeaveUtilizationAnalytics,
    PerformanceCalibrationMetrics,
)

class AnalyticsService:
    @staticmethod
    async def get_hr_overview(db: AsyncSession, org_id: uuid.UUID) -> HROverviewMetrics:
        stmt = select(Employee).where(
            Employee.organization_id == org_id,
            Employee.status != EmploymentStatus.TERMINATED
        )
        employees = (await db.execute(stmt)).scalars().all()

        total = len(employees)
        active = sum(1 for e in employees if e.status == EmploymentStatus.ACTIVE)
        onboarding = sum(1 for e in employees if e.status == EmploymentStatus.ONBOARDING)

        dept_dist: Dict[str, int] = defaultdict(int)
        for e in employees:
            dept_dist[e.department] += 1

        # Calculate onboarding completion rate
        task_stmt = select(OnboardingTask).where(OnboardingTask.organization_id == org_id)
        tasks = (await db.execute(task_stmt)).scalars().all()
        task_total = len(tasks)
        task_completed = sum(1 for t in tasks if t.status in (OnboardingStatus.COMPLETED, OnboardingStatus.WAIVED))
        completion_rate = (task_completed / task_total * 100.0) if task_total > 0 else 100.0

        return HROverviewMetrics(
            total_headcount=total,
            active_employees=active,
            onboarding_employees=onboarding,
            departments_count=len(dept_dist),
            onboarding_completion_rate=round(completion_rate, 1),
            department_distribution=dict(dept_dist)
        )

    @staticmethod
    async def get_leave_utilization(db: AsyncSession, org_id: uuid.UUID) -> LeaveUtilizationAnalytics:
        stmt = select(LeaveRequest, LeavePolicy.name, Employee.department).join(
            LeavePolicy, LeaveRequest.policy_id == LeavePolicy.id
        ).join(
            Employee, LeaveRequest.employee_id == Employee.id
        ).where(
            LeaveRequest.organization_id == org_id
        )
        results = (await db.execute(stmt)).all()

        days_by_policy: Dict[str, float] = defaultdict(float)
        dept_util: Dict[str, float] = defaultdict(float)
        total_taken = 0.0
        pending_count = 0

        for req, pol_name, dept in results:
            if req.status == LeaveStatus.APPROVED:
                total_taken += req.total_days
                days_by_policy[pol_name] += req.total_days
                dept_util[dept] += req.total_days
            elif req.status == LeaveStatus.PENDING:
                pending_count += 1

        return LeaveUtilizationAnalytics(
            total_leave_days_taken=total_taken,
            days_by_policy=dict(days_by_policy),
            department_utilization=dict(dept_util),
            pending_approval_count=pending_count
        )

    @staticmethod
    async def get_performance_calibration(db: AsyncSession, org_id: uuid.UUID) -> PerformanceCalibrationMetrics:
        # Find active cycle
        c_stmt = select(PerformanceCycle).where(
            PerformanceCycle.organization_id == org_id,
            PerformanceCycle.status == CycleStatus.ACTIVE
        ).order_by(PerformanceCycle.start_date.desc())
        cycle = (await db.execute(c_stmt)).scalars().first()

        cycle_id = cycle.id if cycle else None
        cycle_title = cycle.title if cycle else "No Active Cycle"

        # Goals in active cycle
        g_stmt = select(GoalOKR, Employee.department).join(
            Employee, GoalOKR.employee_id == Employee.id
        ).where(GoalOKR.organization_id == org_id)
        if cycle_id:
            g_stmt = g_stmt.where(GoalOKR.cycle_id == cycle_id)

        goal_results = (await db.execute(g_stmt)).all()
        total_goals = len(goal_results)
        achieved_goals = sum(1 for g, d in goal_results if g.progress_percentage >= 100.0)
        goal_comp_rate = (achieved_goals / total_goals * 100.0) if total_goals > 0 else 0.0

        dept_goal_sums: Dict[str, List[float]] = defaultdict(list)
        for g, dept in goal_results:
            dept_goal_sums[dept].append(g.progress_percentage)

        dept_goal_avg = {
            dept: round(sum(scores) / len(scores), 1) for dept, scores in dept_goal_sums.items()
        }

        # Reviews
        r_stmt = select(ReviewFeedback).where(ReviewFeedback.organization_id == org_id)
        if cycle_id:
            r_stmt = r_stmt.where(ReviewFeedback.cycle_id == cycle_id)
        reviews = (await db.execute(r_stmt)).scalars().all()

        return PerformanceCalibrationMetrics(
            cycle_id=cycle_id,
            cycle_title=cycle_title,
            total_reviews_submitted=len(reviews),
            goal_completion_rate=round(goal_comp_rate, 1),
            sentiment_breakdown={"POSITIVE": max(len(reviews) - 1, 0), "NEUTRAL": 1 if len(reviews) > 0 else 0, "NEEDS_IMPROVEMENT": 0},
            department_goal_progress=dept_goal_avg
        )

analytics_service = AnalyticsService()
