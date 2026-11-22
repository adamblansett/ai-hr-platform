from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
import statistics
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.employee import Employee
from backend.app.models.performance import GoalOKR
from backend.app.models.coaching import OneOnOneMeeting, CalibrationSession
from backend.app.schemas.coaching import OneOnOneAgendaGenerateRequest, CalibrationAnalyzeRequest


class CoachingService:
    @staticmethod
    async def generate_1on1_agenda(
        db: AsyncSession,
        org_id: str,
        manager_id: str,
        req: OneOnOneAgendaGenerateRequest
    ) -> OneOnOneMeeting:
        emp_res = await db.execute(select(Employee).where(Employee.id == req.employee_id, Employee.organization_id == org_id))
        emp = emp_res.scalar_one_or_none()
        if not emp:
            raise ValueError("Employee not found")

        # Pull active OKRs
        goals_res = await db.execute(select(GoalOKR).where(GoalOKR.employee_id == req.employee_id))
        goals = goals_res.scalars().all()
        goal_titles = [g.title for g in goals[:2]] if goals else ["Quarterly Priorities"]

        talking_points = [
            f"Review progress on: {', '.join(goal_titles)}",
            "Identify current technical or cross-functional roadblocks",
            "Discuss bandwidth, work-life balance, and cognitive load",
        ]

        if req.focus_area == "CAREER_GROWTH":
            ai_prompts = [
                "What skills or competencies would you like to develop in the next 6 months?",
                "Are there cross-team initiatives or architecture reviews you would like to lead?",
                "Where do you see yourself on our technical leadership rubric?",
            ]
            talking_points.append("Long-term career goals & stretch assignments")
        elif req.focus_area == "PERFORMANCE_INTERVENTION":
            ai_prompts = [
                "What specific support or unblocking do you need from me as your manager?",
                "Let's review the expectations for key delivery milestones and deliverables.",
                "How can we adjust scope or pairing to ensure success?",
            ]
            talking_points.append("Action plan and milestone calibration")
        else:
            ai_prompts = [
                "What was the most rewarding project or milestone you shipped this month?",
                "What processes or tooling are causing unnecessary friction in your daily workflow?",
                "Is there anything I can do differently to better support your day-to-day work?",
            ]

        meeting = OneOnOneMeeting(
            organization_id=org_id,
            manager_id=manager_id,
            employee_id=req.employee_id,
            scheduled_date=req.scheduled_date,
            status="SCHEDULED",
            talking_points=talking_points,
            ai_suggested_prompts=ai_prompts,
            action_items=[],
        )
        db.add(meeting)
        await db.commit()
        await db.refresh(meeting)
        return meeting

    @staticmethod
    async def analyze_calibration(
        db: AsyncSession,
        org_id: str,
        req: CalibrationAnalyzeRequest
    ) -> CalibrationSession:
        ratings = req.ratings
        if not ratings:
            raise ValueError("Ratings list cannot be empty")

        total = len(ratings)
        distribution = {str(i): ratings.count(i) for i in range(1, 6)}
        mean_val = round(statistics.mean(ratings), 2)
        std_dev = round(statistics.stdev(ratings), 2) if total > 1 else 0.0

        biases = []
        recommendations = []

        # Central tendency bias: > 60% rated as 3
        if (distribution.get("3", 0) / total) >= 0.55:
            biases.append("CENTRAL_TENDENCY_BIAS")
            recommendations.append("Over 55% of ratings cluster at level 3. Managers should be coached to differentiate average delivery from high-impact contributions.")

        # Leniency bias: Mean rating > 4.1 or > 50% rated 4 or 5
        high_ratings = distribution.get("4", 0) + distribution.get("5", 0)
        if mean_val >= 4.0 or (high_ratings / total) >= 0.65:
            biases.append("LENIENCY_BIAS")
            recommendations.append("Rating distribution is strongly skewed upwards. Review evidence-based rubric standards for top tier performers.")

        # Harshness bias: Mean rating < 2.5
        if mean_val <= 2.5:
            biases.append("HARSHNESS_BIAS")
            recommendations.append("Rating distribution is heavily skewed downwards. Verify if expectations are calibrated realistically against department tenure.")

        if not biases:
            biases.append("NORMAL_DISTRIBUTION")
            recommendations.append("Distribution aligns closely with standard bell-curve calibration. Well-balanced differentiation.")

        session = CalibrationSession(
            organization_id=org_id,
            cycle_name=req.cycle_name,
            department=req.department,
            total_reviewed=total,
            rating_distribution=distribution,
            detected_biases=biases,
            recommendations=recommendations,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session.mean_rating = mean_val # dynamically attach for response
        return session
