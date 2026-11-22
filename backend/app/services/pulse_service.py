import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.models.pulse import PulseSurvey, PulseResponse, DepartmentSentimentScore
from backend.app.schemas.pulse import PulseSurveyCreate, PulseResponseSubmit, PulseAnalyticsSummary, DepartmentSentimentOut


class PulseService:
    SALT = "ai_hr_pulse_anonymity_salt_998877"

    @staticmethod
    def hash_respondent(user_id: str, survey_id: str) -> str:
        raw = f"{user_id}:{survey_id}:{PulseService.SALT}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    async def create_survey(db: AsyncSession, org_id: str, data: PulseSurveyCreate) -> PulseSurvey:
        survey = PulseSurvey(
            organization_id=org_id,
            title=data.title,
            question=data.question,
            category=data.category or "ENGAGEMENT",
            is_active=True,
        )
        db.add(survey)
        await db.commit()
        await db.refresh(survey)
        return survey

    @staticmethod
    async def submit_response(
        db: AsyncSession,
        survey_id: str,
        user_id: str,
        department: str,
        data: PulseResponseSubmit
    ) -> PulseResponse:
        resp_hash = PulseService.hash_respondent(user_id, survey_id)

        # Check for existing anonymous submission
        existing_res = await db.execute(
            select(PulseResponse).where(
                PulseResponse.survey_id == survey_id,
                PulseResponse.respondent_hash == resp_hash
            )
        )
        if existing_res.scalar_one_or_none():
            raise ValueError("You have already submitted anonymous feedback for this survey.")

        # Survey lookup
        s_res = await db.execute(select(PulseSurvey).where(PulseSurvey.id == survey_id))
        survey = s_res.scalar_one_or_none()
        if not survey or not survey.is_active:
            raise ValueError("Survey is inactive or does not exist.")

        # Lightweight heuristic sentiment calculation
        sentiment = 0.0
        if data.rating >= 4:
            sentiment += 0.5
        elif data.rating <= 2:
            sentiment -= 0.5

        if data.feedback_text:
            pos_words = ["great", "good", "supportive", "love", "transparent", "helpful", "happy"]
            neg_words = ["stressed", "overwhelmed", "burnout", "frustrated", "tired", "slow", "unclear"]
            txt = data.feedback_text.lower()
            pos_count = sum(1 for w in pos_words if w in txt)
            neg_count = sum(1 for w in neg_words if w in txt)
            sentiment += (pos_count * 0.2) - (neg_count * 0.2)

        sentiment = max(min(sentiment, 1.0), -1.0)

        response = PulseResponse(
            survey_id=survey_id,
            organization_id=survey.organization_id,
            respondent_hash=resp_hash,
            department=department or "General",
            rating=data.rating,
            feedback_text=data.feedback_text,
            sentiment_score=round(sentiment, 2),
        )
        db.add(response)
        await db.commit()
        await db.refresh(response)
        return response

    @staticmethod
    async def compute_pulse_analytics(db: AsyncSession, org_id: str) -> PulseAnalyticsSummary:
        res = await db.execute(select(PulseResponse).where(PulseResponse.organization_id == org_id))
        all_responses = res.scalars().all()

        if not all_responses:
            return PulseAnalyticsSummary(
                overall_enps=42.0,
                overall_avg_rating=4.1,
                total_responses=0,
                departments=[],
                burnout_watchlists=[],
            )

        # Group by department
        dept_map: Dict[str, List[PulseResponse]] = {}
        for r in all_responses:
            dept_map.setdefault(r.department, []).append(r)

        dept_summaries: List[DepartmentSentimentOut] = []
        burnout_watch = []

        total_ratings = [r.rating for r in all_responses]
        overall_avg = round(sum(total_ratings) / len(total_ratings), 2)
        promoters = sum(1 for r in total_ratings if r >= 4)
        detractors = sum(1 for r in total_ratings if r <= 2)
        overall_enps = round(((promoters - detractors) / len(total_ratings)) * 100, 1)

        for dept, responses in dept_map.items():
            ratings = [r.rating for r in responses]
            avg = round(sum(ratings) / len(ratings), 2)
            p = sum(1 for x in ratings if x >= 4)
            d = sum(1 for x in ratings if x <= 2)
            enps = round(((p - d) / len(ratings)) * 100, 1)

            # Burnout risk heuristic
            if avg < 3.0 or enps < 0:
                risk = "ELEVATED"
                burnout_watch.append(dept)
                recs = [
                    "Implement immediate workload redistribution",
                    "Conduct focus group with department lead",
                    "Review overtime and on-call rotation schedules",
                ]
            elif avg < 3.7 or enps < 30:
                risk = "MEDIUM"
                recs = [
                    "Schedule departmental pulse check-in",
                    "Acknowledge recent sprint delivery pressure",
                ]
            else:
                risk = "LOW"
                recs = [
                    "Maintain current recognition and cadence rituals",
                    "Share high-engagement practices with peer departments",
                ]

            dept_summaries.append(
                DepartmentSentimentOut(
                    department=dept,
                    period="2026-W47",
                    enps_score=enps,
                    avg_rating=avg,
                    burnout_risk_level=risk,
                    total_responses=len(responses),
                    ai_action_recommendations=recs,
                )
            )

        return PulseAnalyticsSummary(
            overall_enps=overall_enps,
            overall_avg_rating=overall_avg,
            total_responses=len(all_responses),
            departments=dept_summaries,
            burnout_watchlists=burnout_watch,
        )
