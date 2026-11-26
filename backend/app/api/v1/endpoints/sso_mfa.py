from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import require_role
from backend.app.models.employee import Employee, EmployeeRole
from backend.app.schemas.sso_mfa import (
    MFASetupResponse,
    MFAStatusResponse,
    MFAVerifyRequest,
    OIDCAuthorizeResponse,
    SAMLCallbackRequest,
    SAMLCallbackResponse,
    SSOProviderCreate,
    SSOProviderResponse,
)
from backend.app.services.sso_mfa_service import sso_mfa_service

router = APIRouter()


@router.get("/sso/providers", response_model=List[SSOProviderResponse])
def list_sso_providers():
    """List configured Enterprise Identity Providers (Okta / Entra ID / OIDC / SAML 2.0)."""
    return sso_mfa_service.list_providers()


@router.post("/sso/providers", response_model=SSOProviderResponse, status_code=status.HTTP_201_CREATED)
def create_sso_provider(
    payload: SSOProviderCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
):
    """Register a new SAML 2.0 or OIDC Identity Provider for tenant SSO."""
    return sso_mfa_service.create_provider(payload, organization_id=str(current_user.organization_id))


@router.get("/sso/oidc/authorize", response_model=OIDCAuthorizeResponse)
def initiate_oidc_authorize(
    provider_id: Optional[str] = Query(None),
    redirect_uri: str = Query("http://localhost:5173/sso/callback"),
):
    """Generate an OIDC PKCE S256 authorization URL and anti-CSRF state token."""
    try:
        return sso_mfa_service.build_oidc_authorize(provider_id=provider_id, redirect_uri=redirect_uri)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/sso/saml/callback", response_model=SAMLCallbackResponse)
def saml_acs_callback(payload: SAMLCallbackRequest):
    """Validate incoming Base64 SAML 2.0 Assertion Consumer Service payload (XXE-safe)."""
    try:
        return sso_mfa_service.handle_saml_callback(payload.provider_id, payload.saml_response_b64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/mfa/status", response_model=MFAStatusResponse)
def get_mfa_status(employee_id: str = Query("emp-001")):
    """Retrieve MFA (TOTP) enrollment status and remaining backup recovery codes."""
    return sso_mfa_service.get_mfa_status(employee_id=employee_id)


@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(
    employee_id: str = Query("emp-001"),
    email: str = Query("elena.rostova@acme.corp"),
):
    """Provision a new RFC 6238 TOTP secret, otpauth URI, and one-time backup codes."""
    return sso_mfa_service.setup_mfa(employee_id=employee_id, email=email)


@router.post("/mfa/verify", response_model=MFAStatusResponse)
def verify_mfa(payload: MFAVerifyRequest):
    """Verify a 6-digit authenticator TOTP code or recovery code to activate MFA."""
    try:
        return sso_mfa_service.verify_mfa(employee_id=payload.employee_id, code=payload.code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/mfa/disable", response_model=MFAStatusResponse)
def disable_mfa(employee_id: str = Query("emp-001")):
    """Disable TOTP MFA enrollment for the specified employee."""
    return sso_mfa_service.disable_mfa(employee_id=employee_id)
