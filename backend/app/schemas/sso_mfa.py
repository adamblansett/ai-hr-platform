from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SSOProviderCreate(BaseModel):
    provider_type: str = Field(..., pattern="^(SAML_2_0|OIDC)$")
    provider_name: str = Field(..., min_length=2, max_length=100)
    issuer_url: str = Field(..., min_length=8, max_length=500)
    sso_login_url: str = Field(..., min_length=8, max_length=500)
    client_id: Optional[str] = None
    certificate_fingerprint: Optional[str] = None
    enforced_for_admins: bool = True


class SSOProviderResponse(BaseModel):
    id: str
    organization_id: str
    provider_type: str
    provider_name: str
    issuer_url: str
    sso_login_url: str
    client_id: Optional[str] = None
    certificate_fingerprint: Optional[str] = None
    enforced_for_admins: bool
    is_active: bool
    created_at: datetime


class OIDCAuthorizeResponse(BaseModel):
    provider_id: str
    authorization_url: str
    state: str
    code_challenge: str
    code_challenge_method: str = "S256"


class SAMLCallbackRequest(BaseModel):
    provider_id: str
    saml_response_b64: str


class SAMLCallbackResponse(BaseModel):
    verified: bool
    email: str
    issuer: str
    assertion_id: str
    session_token: str


class MFASetupResponse(BaseModel):
    employee_id: str
    secret: str
    otpauth_uri: str
    backup_codes: List[str]
    is_enabled: bool


class MFAVerifyRequest(BaseModel):
    employee_id: str = "emp-001"
    code: str = Field(..., min_length=6, max_length=12)


class MFAStatusResponse(BaseModel):
    employee_id: str
    is_enabled: bool
    enforced_by_policy: bool
    backup_codes_remaining: int
    last_verified_at: Optional[datetime] = None
