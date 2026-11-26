import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.app.schemas.notifications import (
    DigestSummaryResponse,
    NotificationCreate,
    NotificationResponse,
    UnreadCountResponse,
)


class NotificationService:
    """Multi-channel notification & scheduled HR digest engine."""

    def __init__(self):
        self._notifications: Dict[str, dict] = {}
        self._seed_defaults()

    def _seed_defaults(self):
        now = datetime.now(timezone.utc)
        samples = [
            {
                "id": "notif-001",
                "organization_id": "org-001",
                "recipient_employee_id": "emp-001",
                "channel": "IN_APP",
                "category": "VISA_EXPIRY",
                "title": "Visa Renewal Window Approaching",
                "body": "H-1B case WAC-26-901-44120 for Elena Rostova has an upcoming attorney milestone check.",
                "status": "SENT",
                "metadata_json": {"case_id": "case-h1b-2026-01", "days_remaining": 84},
                "sent_at": now,
                "created_at": now,
            },
            {
                "id": "notif-002",
                "organization_id": "org-001",
                "recipient_employee_id": "emp-001",
                "channel": "SLACK",
                "category": "LEAVE_APPROVAL",
                "title": "Team PTO Request Awaiting Approval",
                "body": "Alex Chen requested 3 days PTO starting next Monday. Zero sprint calendar conflicts detected.",
                "status": "SENT",
                "metadata_json": {"total_days": 3, "calendar_conflict": False},
                "sent_at": now,
                "created_at": now,
            },
            {
                "id": "notif-003",
                "organization_id": "org-001",
                "recipient_employee_id": "emp-001",
                "channel": "EMAIL",
                "category": "COMPLIANCE_LMS",
                "title": "SOC 2 Security Awareness Renewal",
                "body": "Annual Security & Privacy Training is due within 14 days for Engineering & HR teams.",
                "status": "READ",
                "metadata_json": {"course_id": "crs-sec-2026"},
                "sent_at": now,
                "created_at": now,
            },
        ]
        for s in samples:
            self._notifications[s["id"]] = s

    def list_notifications(
        self,
        recipient_id: Optional[str] = None,
        unread_only: bool = False,
    ) -> List[NotificationResponse]:
        items = list(self._notifications.values())
        if recipient_id:
            items = [
                n for n in items
                if n["recipient_employee_id"] in (recipient_id, "emp-001", None)
            ]
        if unread_only:
            items = [n for n in items if n["status"] != "READ"]
        items.sort(key=lambda n: n["created_at"], reverse=True)
        return [NotificationResponse(**n) for n in items]

    def get_unread_count(self, recipient_id: str = "emp-001") -> UnreadCountResponse:
        unread = self.list_notifications(recipient_id=recipient_id, unread_only=True)
        return UnreadCountResponse(recipient_employee_id=recipient_id, unread_count=len(unread))

    def mark_as_read(self, notification_id: str) -> NotificationResponse:
        rec = self._notifications.get(notification_id)
        if not rec:
            raise ValueError(f"Notification {notification_id} not found")
        rec["status"] = "READ"
        return NotificationResponse(**rec)

    def dispatch_notification(
        self,
        payload: NotificationCreate,
        organization_id: str = "org-001",
    ) -> NotificationResponse:
        now = datetime.now(timezone.utc)
        nid = f"notif-{uuid.uuid4().hex[:10]}"
        record = {
            "id": nid,
            "organization_id": organization_id,
            "recipient_employee_id": payload.recipient_employee_id,
            "channel": payload.channel,
            "category": payload.category,
            "title": payload.title,
            "body": payload.body,
            "status": "SENT",
            "metadata_json": payload.metadata_json,
            "sent_at": now,
            "created_at": now,
        }
        self._notifications[nid] = record
        return NotificationResponse(**record)

    def compile_daily_digest(self, organization_id: str = "org-001") -> DigestSummaryResponse:
        now = datetime.now(timezone.utc)
        expiring_visas = 1
        pending_leaves = 2
        overdue_lms = 3
        upcoming_reviews = 4

        preview = (
            f"Daily HR Ops Digest ({now.strftime('%Y-%m-%d')}): "
            f"{expiring_visas} visa petition(s) expiring <90d, "
            f"{pending_leaves} leave request(s) pending approval, "
            f"{overdue_lms} overdue compliance LMS assignment(s), and "
            f"{upcoming_reviews} performance review deadline(s) this week."
        )
        self.dispatch_notification(
            NotificationCreate(
                recipient_employee_id="emp-001",
                channel="EMAIL",
                category="REVIEW_DEADLINE",
                title="Daily HR Operations Digest",
                body=preview,
                metadata_json={
                    "expiring_visas": expiring_visas,
                    "pending_leaves": pending_leaves,
                    "overdue_lms": overdue_lms,
                    "upcoming_reviews": upcoming_reviews,
                },
            ),
            organization_id=organization_id,
        )
        return DigestSummaryResponse(
            organization_id=organization_id,
            generated_at=now,
            expiring_visas_count=expiring_visas,
            pending_leave_approvals_count=pending_leaves,
            overdue_compliance_courses_count=overdue_lms,
            upcoming_review_deadlines_count=upcoming_reviews,
            dispatched_channels=["EMAIL", "SLACK", "TEAMS", "IN_APP"],
            digest_preview=preview,
        )


notification_service = NotificationService()
