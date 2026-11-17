import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    pii_redacted: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedAuditLogsResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
    total_pages: int
