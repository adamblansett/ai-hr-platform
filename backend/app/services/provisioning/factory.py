from typing import Optional, Dict, Any
from backend.app.services.provisioning.base import BaseProvisioningAdapter
from backend.app.services.provisioning.mock_adapter import MockProvisioningAdapter
from backend.app.services.provisioning.scim_adapter import SCIMProvisioningAdapter
from backend.app.services.provisioning.google_workspace_adapter import GoogleWorkspaceProvisioningAdapter

# Singleton mock instance for in-memory session persistence
_shared_mock_adapter = MockProvisioningAdapter()

def get_provisioning_adapter(
    provider_type: str = "mock",
    config: Optional[Dict[str, Any]] = None
) -> BaseProvisioningAdapter:
    """
    Factory function returning the configured provisioning adapter.
    Supports:
    - 'mock': Local dev & sandbox testing
    - 'scim' or 'okta': Enterprise SCIM 2.0 (Okta, Entra ID)
    - 'google_workspace': Google Workspace Admin SDK Directory API
    """
    cfg = config or {}
    provider = provider_type.lower()

    if provider in ("mock", "local", "stub"):
        return _shared_mock_adapter

    elif provider in ("scim", "okta"):
        scim_url = cfg.get("scim_base_url") or "https://example.okta.com/scim/v2"
        token = cfg.get("bearer_token") or "mock-bearer-token"
        return SCIMProvisioningAdapter(scim_base_url=scim_url, bearer_token=token, provider_name="okta-scim")

    elif provider in ("google", "google_workspace", "gsuite"):
        token = cfg.get("access_token") or "mock-google-token"
        customer_id = cfg.get("customer_id", "my_customer")
        org_unit = cfg.get("org_unit_path", "/")
        return GoogleWorkspaceProvisioningAdapter(access_token=token, customer_id=customer_id, org_unit_path=org_unit)

    # Default fallback to mock adapter
    return _shared_mock_adapter
