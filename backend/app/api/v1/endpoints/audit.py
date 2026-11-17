import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.schemas.audit import PaginatedAuditLogsResponse
from backend.app.services.audit_service import audit_service

router = APIRouter()

@router.get("/", response_model=PaginatedAuditLogsResponse, summary="Query audit logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    actor_id: Optional[uuid.UUID] = None,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    items, total, total_pages = await audit_service.list_audit_logs(
        db=db,
        org_id=current_user.organization_id,
        page=page,
        size=size,
        action=action,
        entity_type=entity_type,
        actor_id=actor_id
    )
    return PaginatedAuditLogsResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )
