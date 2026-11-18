import uuid
from typing import Dict, Any

class TeamsService:
    @staticmethod
    def build_leave_adaptive_card(
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
        Builds Microsoft Teams Adaptive Card format.
        """
        card = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "🌴 Time-Off Request Pending Approval",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Employee", "value": f"{employee_name} ({department})"},
                        {"title": "Policy", "value": policy_name},
                        {"title": "Dates", "value": f"{start_date} to {end_date} ({total_days} days)"},
                        {"title": "Reason", "value": reason},
                        {"title": "Calendar Conflict", "value": "Yes - Overlap detected" if conflict_detected else "None"}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Approve",
                    "data": {"action": "APPROVE", "request_id": str(request_id)}
                },
                {
                    "type": "Action.Submit",
                    "title": "Reject",
                    "data": {"action": "REJECT", "request_id": str(request_id)}
                }
            ]
        }
        return card

teams_service = TeamsService()
