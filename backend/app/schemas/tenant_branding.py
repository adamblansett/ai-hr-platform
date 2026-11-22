from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TenantBrandingUpdate(BaseModel):
    company_name: Optional[str] = None
    custom_domain: Optional[str] = None
    primary_color_hex: Optional[str] = None
    secondary_color_hex: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    support_email: Optional[str] = None
    portal_title: Optional[str] = None


class TenantBrandingResponse(BaseModel):
    id: str
    organization_id: str
    company_name: str
    custom_domain: str
    custom_domain_verified: bool
    ssl_cert_status: str
    primary_color_hex: str
    secondary_color_hex: str
    logo_url: str
    favicon_url: str
    support_email: str
    portal_title: str
    kms_key_id: str
    updated_at: datetime


class DomainVerificationResult(BaseModel):
    custom_domain: str
    dns_cname_target: str
    dns_txt_verification_record: str
    is_verified: bool
    ssl_cert_status: str
    message: str
