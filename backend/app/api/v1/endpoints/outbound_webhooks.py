from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone
import json

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.outbound_webhook import WebhookSubscription, WebhookDeliveryLog
from backend.app.schemas.outbound_webhook import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionOut,
    WebhookDeliveryLogOut,
    WebhookTestPingResponse,
)
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.outbound_webhook_service import OutboundWebhookService

router = APIRouter()


@router.post("/subscriptions", response_model=WebhookSubscriptionOut, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    sub_in: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Register an outbound webhook subscription (Workday, ADP, Gusto, internal ERP)."""
    sub = await OutboundWebhookService.create_subscription(
        db,
        org_id=current_user.organization_id,
        target_url=sub_in.target_url,
        event_types=sub_in.event_types,
        description=sub_in.description,
    )
    return sub


@router.get("/subscriptions", response_model=List[WebhookSubscriptionOut])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """List all registered outbound webhook subscriptions for the organization."""
    res = await db.execute(
        select(WebhookSubscription).where(
            WebhookSubscription.organization_id == current_user.organization_id
        )
    )
    return res.scalars().all()


@router.delete("/subscriptions/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    sub_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Remove an outbound webhook subscription."""
    res = await db.execute(
        select(WebhookSubscription).where(
            WebhookSubscription.id == sub_id,
            WebhookSubscription.organization_id == current_user.organization_id,
        )
    )
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook subscription not found")
    await db.delete(sub)
    await db.commit()
    return None


@router.post("/subscriptions/{sub_id}/test-ping", response_model=WebhookTestPingResponse)
async def test_ping_subscription(
    sub_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Dispatch a test ping payload signed with HMAC-SHA256."""
    res = await db.execute(
        select(WebhookSubscription).where(
            WebhookSubscription.id == sub_id,
            WebhookSubscription.organization_id == current_user.organization_id,
        )
    )
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook subscription not found")

    test_payload = {
        "event": "system.ping",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"message": "Test webhook delivery from ai-hr-platform"},
    }
    payload_bytes = json.dumps(test_payload, sort_keys=True).encode("utf-8")
    signature = OutboundWebhookService.sign_payload(sub.secret_key, payload_bytes)

    return WebhookTestPingResponse(
        status="DELIVERY_SIMULATED",
        target_url=sub.target_url,
        signature_header=f"sha256={signature}",
        test_event="system.ping",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/subscriptions/{sub_id}/logs", response_model=List[WebhookDeliveryLogOut])
async def list_delivery_logs(
    sub_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """View delivery attempt logs for a subscription."""
    res = await db.execute(
        select(WebhookDeliveryLog)
        .where(WebhookDeliveryLog.subscription_id == sub_id)
        .order_by(WebhookDeliveryLog.delivered_at.desc())
        .limit(50)
    )
    return res.scalars().all()
