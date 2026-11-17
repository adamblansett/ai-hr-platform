import math
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.audit import AuditLog
from backend.app.services.pii_scrubber import PIIScrubber

class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        org_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        actor_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        auto_scrub_pii: bool = True
    ) -> AuditLog:
        raw_details = details or {}
        scrubbed_details = raw_details
        pii_found = False

        if auto_scrub_pii:
            import json
            details_str = json.dumps(raw_details)
            clean_str, pii_found = PIIScrubber.redact(details_str)
            scrubbed_details = json.loads(clean_str)

        audit_entry = AuditLog(
            organization_id=org_id,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=scrubbed_details,
            ip_address=ip_address,
            user_agent=user_agent,
            pii_redacted=True
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    async def list_audit_logs(
        db: AsyncSession,
        org_id: uuid.UUID,
        page: int = 1,
        size: int = 50,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[AuditLog], int, int]:
        query = select(AuditLog).where(AuditLog.organization_id == org_id)

        if action:
            query = query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        if actor_id:
            query = query.where(AuditLog.actor_id == actor_id)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0
        total_pages = math.ceil(total / size) if size > 0 else 1

        offset = (page - 1) * size
        paginated_stmt = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(size)
        items = (await db.execute(paginated_stmt)).scalars().all()

        return list(items), total, total_pages

audit_service = AuditService()
