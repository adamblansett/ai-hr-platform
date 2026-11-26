from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.notifications import (
    DigestSummaryResponse,
    NotificationCreate,
    NotificationResponse,
    UnreadCountResponse,
)
from backend.app.services.notification_service import notification_service

router = APIRouter()


@router.get("/me", response_model=List[NotificationResponse])
def list_my_notifications(
    recipient_id: Optional[str] = Query("emp-001"),
    unread_only: bool = Query(False),
):
    """List multi-channel notifications for the current employee."""
    return notification_service.list_notifications(recipient_id=recipient_id, unread_only=unread_only)


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(recipient_id: str = Query("emp-001")):
    """Return unread notification count badge for sidebar/top-bar indicators."""
    return notification_service.get_unread_count(recipient_id=recipient_id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: str):
    """Mark a notification item as read."""
    try:
        return notification_service.mark_as_read(notification_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/dispatch", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def dispatch_notification(payload: NotificationCreate):
    """Dispatch an ad-hoc notification across Email, Slack, MS Teams, or In-App."""
    return notification_service.dispatch_notification(payload)


@router.post("/digest/trigger", response_model=DigestSummaryResponse)
def trigger_daily_digest(organization_id: str = Query("org-001")):
    """Compile and dispatch an on-demand Daily HR Operations Digest."""
    return notification_service.compile_daily_digest(organization_id=organization_id)
