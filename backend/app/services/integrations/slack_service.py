import json
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.leave import LeaveDecisionRequest
from backend.app.models.leave import LeaveStatus
from backend.app.services.policy_rag_service import policy_rag_service
from backend.app.schemas.policy import PolicyQuestionRequest
from backend.app.services.leave_service import leave_service

class SlackService:
    @staticmethod
    def build_leave_approval_blocks(
        request_id: uuid.UUID,
        employee_name: str,
        department: str,
        policy_name: str,
        start_date: str,
        end_date: str,
        total_days: float,
        reason: str,
        conflict_detected: bool
    ) -> Dict[str, Any]:
        """
        Constructs a Slack Block Kit interactive message for managers to approve or reject leave requests.
        """
        conflict_warning = ""
        if conflict_detected:
            conflict_warning = "\n⚠️ *Calendar Conflict:* Other team members in your department have overlapping approved time off."

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🌴 New Time-Off Request Pending Approval"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Employee:*\n{employee_name} ({department})"},
                    {"type": "mrkdwn", "text": f"*Policy:*\n{policy_name}"},
                    {"type": "mrkdwn", "text": f"*Dates:*\n{start_date} to {end_date} ({total_days} days)"},
                    {"type": "mrkdwn", "text": f"*Reason:*\n{reason}"}
                ]
            }
        ]

        if conflict_detected:
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": conflict_warning}]
            })

        blocks.append({
            "type": "actions",
            "block_id": f"leave_action_{request_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": json.dumps({"action": "APPROVE", "request_id": str(request_id)})
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Reject"},
                    "style": "danger",
                    "value": json.dumps({"action": "REJECT", "request_id": str(request_id)})
                }
            ]
        })

        return {"blocks": blocks}

    @staticmethod
    async def handle_ask_hr_command(
        db: AsyncSession,
        org_id: uuid.UUID,
        question: str
    ) -> Dict[str, Any]:
        """
        Executes grounded Policy RAG and returns a rich Slack Block Kit response with citations.
        """
        req = PolicyQuestionRequest(question=question)
        answer_resp = await policy_rag_service.query_policy_rag(db, org_id, req)

        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Question:* {question}\n\n*Answer:*\n{answer_resp.answer}"}
            }
        ]

        if answer_resp.citations:
            citations_text = "*Sources Referenced:*\n"
            for c in answer_resp.citations:
                citations_text += f"• *{c.title}* (Section {c.chunk_index + 1}) — {round(c.relevance_score * 100)}% match\n"
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": citations_text}]
            })

        return {"response_type": "in_channel", "blocks": blocks}

    @staticmethod
    async def handle_interactive_action(
        db: AsyncSession,
        org_id: uuid.UUID,
        approver_id: uuid.UUID,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        req_id = uuid.UUID(action_data["request_id"])
        decision = action_data["action"] # APPROVE or REJECT
        status_enum = LeaveStatus.APPROVED if decision == "APPROVE" else LeaveStatus.REJECTED

        updated_req = await leave_service.process_decision(
            db=db,
            org_id=org_id,
            approver_id=approver_id,
            request_id=req_id,
            decision_data=LeaveDecisionRequest(
                status=status_enum,
                decision_reason=f"Decided via Slack interactive card ({decision})"
            )
        )

        return {
            "text": f"✅ Leave request {req_id} was successfully marked as *{status_enum.value}*."
        }

slack_service = SlackService()
