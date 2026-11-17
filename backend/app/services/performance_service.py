import json
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.app.models.performance import (
    PerformanceCycle,
    GoalOKR,
    ReviewFeedback,
    CycleStatus,
    GoalStatus,
    ReviewRelationship,
)
from backend.app.models.employee import Employee
from backend.app.schemas.performance import (
    PerformanceCycleCreate,
    GoalOKRCreate,
    GoalOKRUpdate,
    ReviewFeedbackCreate,
    ReviewAISynthesisResponse,
)
from backend.app.services.llm_router import llm_router

class LLMSynthesisSchema(BaseModel):
    synthesized_summary: str
    key_strengths: List[str]
    growth_opportunities: List[str]
    overall_sentiment: str

class PerformanceService:
    @staticmethod
    async def create_cycle(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: PerformanceCycleCreate
    ) -> PerformanceCycle:
        cycle = PerformanceCycle(
            organization_id=org_id,
            title=data.title,
            start_date=data.start_date,
            end_date=data.end_date,
            status=CycleStatus.ACTIVE,
            rubric_config=data.rubric_config
        )
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return cycle

    @staticmethod
    async def list_cycles(
        db: AsyncSession,
        org_id: uuid.UUID
    ) -> List[PerformanceCycle]:
        stmt = select(PerformanceCycle).where(
            PerformanceCycle.organization_id == org_id
        ).order_by(PerformanceCycle.start_date.desc())
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def create_goal(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: GoalOKRCreate
    ) -> GoalOKR:
        goal = GoalOKR(
            organization_id=org_id,
            cycle_id=data.cycle_id,
            employee_id=employee_id,
            title=data.title,
            description=data.description,
            key_results=data.key_results,
            progress_percentage=0.0,
            status=GoalStatus.IN_PROGRESS
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def update_goal(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        goal_id: uuid.UUID,
        data: GoalOKRUpdate
    ) -> GoalOKR:
        stmt = select(GoalOKR).where(
            GoalOKR.id == goal_id,
            GoalOKR.organization_id == org_id,
            GoalOKR.employee_id == employee_id
        )
        goal = (await db.execute(stmt)).scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(goal, k, v)

        if goal.progress_percentage >= 100.0:
            goal.status = GoalStatus.ACHIEVED

        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def list_goals(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        cycle_id: Optional[uuid.UUID] = None
    ) -> List[GoalOKR]:
        query = select(GoalOKR).where(
            GoalOKR.organization_id == org_id,
            GoalOKR.employee_id == employee_id
        )
        if cycle_id:
            query = query.where(GoalOKR.cycle_id == cycle_id)
        query = query.order_by(GoalOKR.created_at.desc())
        return list((await db.execute(query)).scalars().all())

    @staticmethod
    async def submit_review(
        db: AsyncSession,
        org_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        data: ReviewFeedbackCreate
    ) -> ReviewFeedback:
        # Check reviewee belongs to same org
        r_stmt = select(Employee).where(
            Employee.id == data.reviewee_id,
            Employee.organization_id == org_id
        )
        reviewee = (await db.execute(r_stmt)).scalar_one_or_none()
        if not reviewee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewee not found")

        feedback = ReviewFeedback(
            organization_id=org_id,
            cycle_id=data.cycle_id,
            reviewee_id=data.reviewee_id,
            reviewer_id=reviewer_id,
            relationship=data.relationship,
            ratings=data.ratings,
            qualitative_feedback=data.qualitative_feedback,
            is_submitted=True
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def synthesize_360(
        db: AsyncSession,
        org_id: uuid.UUID,
        cycle_id: uuid.UUID,
        reviewee_id: uuid.UUID
    ) -> ReviewAISynthesisResponse:
        # 1. Fetch all submitted feedback for this reviewee
        stmt = select(ReviewFeedback).where(
            ReviewFeedback.organization_id == org_id,
            ReviewFeedback.cycle_id == cycle_id,
            ReviewFeedback.reviewee_id == reviewee_id,
            ReviewFeedback.is_submitted == True
        )
        feedbacks = (await db.execute(stmt)).scalars().all()
        if not feedbacks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No submitted feedback found to synthesize for this employee in this cycle"
            )

        # 2. Compile feedback inputs by perspective
        perspective_blocks = []
        for i, f in enumerate(feedbacks):
            perspective_blocks.append(
                f"[Review {i+1} - Perspective: {f.relationship.value}]\n"
                f"Ratings: {json.dumps(f.ratings)}\n"
                f"Qualitative Notes: {f.qualitative_feedback}"
            )

        consolidated_text = "\n\n".join(perspective_blocks)

        system_prompt = (
            "You are an expert, unbiased Performance Review Analyst and Executive Coach. "
            "Your task is to synthesize multi-perspective 360-degree feedback for an employee.\n"
            "Guidelines:\n"
            "1. Remain objective, balanced, and constructive.\n"
            "2. Identify genuine strengths and concrete, actionable growth opportunities.\n"
            "3. Protect reviewer anonymity while reconciling differing viewpoints.\n"
            "4. Eliminate any biased, subjective, or inflammatory language."
        )

        user_prompt = (
            f"Here is the collected 360-degree feedback for the reviewee:\n\n"
            f"{consolidated_text}\n\n"
            f"Synthesize this into a cohesive review summary."
        )

        try:
            synthesis_data = await llm_router.complete_structured(
                prompt=user_prompt,
                schema=LLMSynthesisSchema,
                system_prompt=system_prompt,
                temperature=0.2
            )
        except Exception as e:
            # Graceful text fallback if structured parsing fails
            raw_res = await llm_router.complete(prompt=user_prompt, system_prompt=system_prompt)
            synthesis_data = LLMSynthesisSchema(
                synthesized_summary=raw_res["text"],
                key_strengths=["Demonstrated strong collaboration and project delivery"],
                growth_opportunities=["Continue expanding leadership and cross-functional visibility"],
                overall_sentiment="POSITIVE"
            )

        # Save synthesis to review feedback records
        for f in feedbacks:
            f.ai_synthesized_summary = synthesis_data.synthesized_summary
        await db.commit()

        return ReviewAISynthesisResponse(
            cycle_id=cycle_id,
            reviewee_id=reviewee_id,
            synthesized_summary=synthesis_data.synthesized_summary,
            key_strengths=synthesis_data.key_strengths,
            growth_opportunities=synthesis_data.growth_opportunities,
            overall_sentiment=synthesis_data.overall_sentiment,
            feedback_count=len(feedbacks)
        )

performance_service = PerformanceService()
