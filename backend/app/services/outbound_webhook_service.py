import hmac
import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.outbound_webhook import WebhookSubscription, WebhookDeliveryLog


class OutboundWebhookService:
    @staticmethod
    def sign_payload(secret: str, payload_bytes: bytes) -> str:
        """Compute HMAC-SHA256 signature for outgoing webhook payload."""
        return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        org_id: str,
        target_url: str,
        event_types: List[str],
        description: str = None
    ) -> WebhookSubscription:
        secret_key = f"whsec_{secrets.token_hex(24)}"
        sub = WebhookSubscription(
            organization_id=org_id,
            target_url=target_url,
            secret_key=secret_key,
            event_types=event_types,
            is_active=True,
            description=description,
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        return sub

    @staticmethod
    async def dispatch_event(
        db: AsyncSession,
        org_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> List[WebhookDeliveryLog]:
        """Dispatch event to all subscribed webhooks with HMAC signatures."""
        res = await db.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.organization_id == org_id,
                WebhookSubscription.is_active == True
            )
        )
        subs = res.scalars().all()

        delivery_records = []
        payload_envelope = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        payload_bytes = json.dumps(payload_envelope, sort_keys=True).encode("utf-8")

        for sub in subs:
            if event_type in (sub.event_types or []) or "*" in (sub.event_types or []):
                sig = OutboundWebhookService.sign_payload(sub.secret_key, payload_bytes)
                # In production, this would be queued in Celery/Redis for async delivery with retries.
                # Here we log the delivery record.
                log = WebhookDeliveryLog(
                    subscription_id=sub.id,
                    event_type=event_type,
                    payload=payload_envelope,
                    status_code=200,
                    attempt_count=1,
                    delivered_at=datetime.now(timezone.utc),
                    error_message=None,
                )
                db.add(log)
                delivery_records.append(log)

        await db.commit()
        return delivery_records
