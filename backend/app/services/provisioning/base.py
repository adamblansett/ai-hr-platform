from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ProvisioningStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    SIMULATED = "SIMULATED"

class ProvisioningResult(BaseModel):
    external_id: Optional[str] = None
    status: ProvisioningStatus
    provider: str
    email_provisioned: str
    assigned_groups: List[str] = Field(default_factory=list)
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

class BaseProvisioningAdapter(ABC):
    """
    Abstract base interface for Identity Provider (IdP) provisioning adapters.
    """

    @abstractmethod
    async def provision_employee(self, employee_data: Dict[str, Any]) -> ProvisioningResult:
        """
        Creates an employee identity in the target IdP (Okta, Google Workspace, or Mock).
        """
        pass

    @abstractmethod
    async def deprovision_employee(self, external_id: str) -> ProvisioningResult:
        """
        Suspends or removes employee access in the IdP upon termination or leave.
        """
        pass

    @abstractmethod
    async def update_employee_groups(self, external_id: str, groups: List[str]) -> ProvisioningResult:
        """
        Updates role-based security groups or organizational units.
        """
        pass

    @abstractmethod
    async def get_user_status(self, external_id: str) -> Dict[str, Any]:
        """
        Fetches current live status and metadata for an identity.
        """
        pass
