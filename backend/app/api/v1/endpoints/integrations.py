import json
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.api.deps import get_db
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.services.integrations.slack_service import slack_service
from backend.app.services.integrations.teams_service import teams_service

router = APIRouter()

@router.post("/slack/command", summary="Slack slash command webhook (/ask-hr)")
async def handle_slack_command(
    request: Request,
    command: str = Form(...),
    text: str = Form(""),
    user_id: str = Form(...),
    user_name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # In a production app, verify Slack Signing Secret via request headers
    # Lookup or default organization (Acme demo org)
    default_org_id = uuid.UUID("11111111-1111-1111-1111-111111111111")

    if command == "/ask-hr":
        if not text.strip():
            return {
                "text": "Please provide a question, e.g. `/ask-hr What is the PTO rollover policy?`"
            }
        return await slack_service.handle_ask_hr_command(db, default_org_id, text)

    return {"text": f"Unknown command: {command}"}

@router.post("/slack/actions", summary="Slack interactive Block Kit actions handler")
async def handle_slack_actions(
    payload: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    data = json.loads(payload)
    actions = data.get("actions", [])
    if not actions:
        return {"text": "No action received"}

    action_value = json.loads(actions[0].get("value", "{}"))
    default_org_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    
    # Resolve acting manager in the org
    stmt = select(Employee).where(
        Employee.organization_id == default_org_id,
        Employee.role == EmployeeRole.PEOPLE_MANAGER
    )
    approver = (await db.execute(stmt)).scalars().first()
    approver_id = approver.id if approver else uuid.uuid4()

    return await slack_service.handle_interactive_action(
        db=db,
        org_id=default_org_id,
        approver_id=approver_id,
        action_data=action_value
    )

@router.post("/teams/webhook", summary="Microsoft Teams Adaptive Card action handler")
async def handle_teams_webhook(
    card_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    action = card_data.get("action")
    req_id_str = card_data.get("request_id")
    if not action or not req_id_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing action or request_id")

    default_org_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    stmt = select(Employee).where(
        Employee.organization_id == default_org_id,
        Employee.role == EmployeeRole.PEOPLE_MANAGER
    )
    approver = (await db.execute(stmt)).scalars().first()
    approver_id = approver.id if approver else uuid.uuid4()

    return await slack_service.handle_interactive_action(
        db=db,
        org_id=default_org_id,
        approver_id=approver_id,
        action_data={"action": action, "request_id": req_id_str}
    )
