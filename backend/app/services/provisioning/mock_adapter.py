import uuid
from typing import Dict, Any, List
from backend.app.services.provisioning.base import BaseProvisioningAdapter, ProvisioningResult, ProvisioningStatus

class MockProvisioningAdapter(BaseProvisioningAdapter):
    """
    Mock IdP adapter for local development, automated testing, and offline sandbox environments.
    Simulates identity creation, group membership assignment, and status queries.
    """

    def __init__(self):
        # In-memory identity registry: external_id -> user_dict
        self._registry: Dict[str, Dict[str, Any]] = {}

    async def provision_employee(self, employee_data: Dict[str, Any]) -> ProvisioningResult:
        email = employee_data.get("email", "mock.user@internal.dev")
        first_name = employee_data.get("first_name", "Jane")
        last_name = employee_data.get("last_name", "Doe")
        department = employee_data.get("department", "Engineering")
        
        external_id = f"mock_idp_{uuid.uuid4().hex[:12]}"
        default_groups = ["all-employees", f"dept-{department.lower().replace(' ', '-')}"]

        self._registry[external_id] = {
            "external_id": external_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "department": department,
            "groups": default_groups,
            "active": True
        }

        return ProvisioningResult(
            external_id=external_id,
            status=ProvisioningStatus.SIMULATED,
            provider="mock-idp",
            email_provisioned=email,
            assigned_groups=default_groups,
            raw_response={"mock_action": "created", "stored_in_memory": True}
        )

    async def deprovision_employee(self, external_id: str) -> ProvisioningResult:
        if external_id in self._registry:
            self._registry[external_id]["active"] = False
            return ProvisioningResult(
                external_id=external_id,
                status=ProvisioningStatus.SIMULATED,
                provider="mock-idp",
                email_provisioned=self._registry[external_id]["email"],
                raw_response={"mock_action": "deactivated"}
            )
        return ProvisioningResult(
            external_id=external_id,
            status=ProvisioningStatus.FAILED,
            provider="mock-idp",
            email_provisioned="unknown",
            error_message=f"External identity {external_id} not found in mock registry"
        )

    async def update_employee_groups(self, external_id: str, groups: List[str]) -> ProvisioningResult:
        if external_id in self._registry:
            self._registry[external_id]["groups"] = groups
            return ProvisioningResult(
                external_id=external_id,
                status=ProvisioningStatus.SIMULATED,
                provider="mock-idp",
                email_provisioned=self._registry[external_id]["email"],
                assigned_groups=groups,
                raw_response={"mock_action": "groups_updated"}
            )
        return ProvisioningResult(
            external_id=external_id,
            status=ProvisioningStatus.FAILED,
            provider="mock-idp",
            email_provisioned="unknown",
            error_message=f"External identity {external_id} not found"
        )

    async def get_user_status(self, external_id: str) -> Dict[str, Any]:
        return self._registry.get(external_id, {"found": False})
