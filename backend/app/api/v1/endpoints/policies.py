import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.core.config import settings
from backend.app.core.rate_limit import rate_limit
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.models.policy import PolicyDocument, PolicyAcknowledgment
from backend.app.schemas.policy import (
    PolicyDocumentCreate,
    PolicyDocumentResponse,
    PolicyQuestionRequest,
    PolicyAnswerResponse,
    PolicyAcknowledgmentRequest,
    PolicyAcknowledgmentResponse,
)
from backend.app.services.policy_rag_service import policy_rag_service

router = APIRouter()

@router.get("/", response_model=List[PolicyDocumentResponse], summary="List published policies")
async def list_policies(
    category: Optional[str] = None,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(PolicyDocument).where(
        PolicyDocument.organization_id == current_user.organization_id,
        PolicyDocument.is_active == True,
        PolicyDocument.chunk_index == 0 # Return first chunk / document header representation
    )
    if category:
        query = query.where(PolicyDocument.category == category)
    query = query.order_by(PolicyDocument.title.asc())

    docs = (await db.execute(query)).scalars().all()
    return list(docs)

@router.post("/upload", response_model=List[PolicyDocumentResponse], status_code=status.HTTP_201_CREATED, summary="Upload & embed policy document")
async def upload_policy(
    data: PolicyDocumentCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    docs = await policy_rag_service.ingest_policy(
        db=db,
        org_id=current_user.organization_id,
        data=data
    )
    return docs

@router.post(
    "/chat",
    response_model=PolicyAnswerResponse,
    summary="Grounded Policy RAG Q&A Assistant",
    dependencies=[Depends(rate_limit("policy_chat", settings.RATE_LIMIT_AI_PER_MINUTE, 60))],
)
async def chat_policy_rag(
    request_data: PolicyQuestionRequest,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await policy_rag_service.query_policy_rag(
        db=db,
        org_id=current_user.organization_id,
        req=request_data
    )

@router.post("/{policy_id}/acknowledge", response_model=PolicyAcknowledgmentResponse, summary="Electronically sign policy acknowledgment")
async def acknowledge_policy(
    policy_id: uuid.UUID,
    data: PolicyAcknowledgmentRequest,
    request: Request,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    ack = await policy_rag_service.acknowledge_policy(
        db=db,
        org_id=current_user.organization_id,
        employee_id=current_user.id,
        policy_id=policy_id,
        signature_name=data.signature_name,
        ip_address=client_ip
    )
    return ack

@router.get("/{policy_id}/acknowledgments", response_model=List[PolicyAcknowledgmentResponse], summary="List compliance signatures for policy")
async def list_policy_acknowledgments(
    policy_id: uuid.UUID,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PolicyAcknowledgment).where(
        PolicyAcknowledgment.policy_id == policy_id
    ).order_by(PolicyAcknowledgment.acknowledged_at.desc())
    acks = (await db.execute(stmt)).scalars().all()
    return list(acks)
