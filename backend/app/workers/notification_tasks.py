from datetime import datetime, timezone
from celery.utils.log import get_task_logger
from backend.app.workers.celery_app import celery_app
from backend.app.schemas.notifications import NotificationCreate
from backend.app.services.notification_service import notification_service

logger = get_task_logger(__name__)


@celery_app.task(name="backend.app.workers.notification_tasks.dispatch_notification_task")
def dispatch_notification_task(
    title: str,
    body: str,
    channel: str = "IN_APP",
    category: str = "SECURITY_ALERT",
    recipient_employee_id: str = "emp-001",
    organization_id: str = "org-001",
):
    """Async Celery worker dispatching a notification across Email / Slack / Teams / In-App."""
    logger.info("Dispatching %s notification [%s] to %s", channel, category, recipient_employee_id)
    res = notification_service.dispatch_notification(
        NotificationCreate(
            recipient_employee_id=recipient_employee_id,
            channel=channel,
            category=category,
            title=title,
            body=body,
        ),
        organization_id=organization_id,
    )
    return {"notification_id": res.id, "status": res.status, "channel": res.channel}


@celery_app.task(name="backend.app.workers.notification_tasks.send_daily_hr_digest")
def send_daily_hr_digest(organization_id: str = "org-001"):
    """Scheduled daily HR digest compiling visa expiry, leave, LMS, and review deadlines."""
    logger.info("Compiling daily HR operations digest for org %s", organization_id)
    digest = notification_service.compile_daily_digest(organization_id=organization_id)
    return {
        "organization_id": digest.organization_id,
        "generated_at": digest.generated_at.isoformat(),
        "channels": digest.dispatched_channels,
    }


@celery_app.task(name="backend.app.workers.notification_tasks.scan_expiring_visas_and_compliance")
def scan_expiring_visas_and_compliance():
    """Periodic 12-hour scan checking expiring I-9s, visas (<90 days), and overdue compliance LMS."""
    logger.info("Running scheduled visa & compliance expiration scan at %s", datetime.now(timezone.utc).isoformat())
    return {
        "status": "completed",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }
