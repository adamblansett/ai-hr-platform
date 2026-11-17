from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "ai_hr_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "check-onboarding-due-dates-daily": {
            "task": "backend.app.workers.onboarding_tasks.check_onboarding_deadlines",
            "schedule": 86400.0, # Every 24 hours
        },
    },
)

celery_app.autodiscover_tasks([
    "backend.app.workers.onboarding_tasks",
])
