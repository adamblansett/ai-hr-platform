from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.app.api.deps import get_db
from backend.app.schemas.webhook import RecruiterOfferAcceptedWebhook, RecruiterWebhookResponse
from backend.app.services.webhook_service import webhook_service

router = APIRouter()

@router.post(
    "/recruiter/offer-accepted",
    response_model=RecruiterWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest candidate offer acceptance from ai-recruiter"
)
async def handle_recruiter_offer_accepted(
    request: Request,
    x_recruiter_signature: Optional[str] = Header(None, alias="X-Recruiter-Signature"),
    db: AsyncSession = Depends(get_db)
):
    raw_body = await request.body()
    
    # Verify HMAC-SHA256 signature
    is_valid = webhook_service.verify_signature(raw_body, x_recruiter_signature)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Recruiter-Signature HMAC header"
        )

    # Parse and validate JSON payload
    try:
        import json
        payload_dict = json.loads(raw_body.decode("utf-8"))
        payload = RecruiterOfferAcceptedWebhook.model_validate(payload_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Malformed webhook JSON payload: {str(e)}"
        )

    client_ip = request.client.host if request.client else None
    return await webhook_service.process_offer_accepted(
        db=db,
        payload=payload,
        ip_address=client_ip
    )
