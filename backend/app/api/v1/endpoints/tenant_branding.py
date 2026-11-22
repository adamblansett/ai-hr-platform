from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.tenant_branding import (
    TenantBrandingUpdate,
    TenantBrandingResponse,
    DomainVerificationResult,
)
from backend.app.services.tenant_branding_service import tenant_branding_service

router = APIRouter()


@router.get("/", response_model=TenantBrandingResponse)
def get_tenant_branding(organization_id: str = Query("org-001")):
    """Get tenant white-label configuration, custom domain, and brand theme."""
    return tenant_branding_service.get_branding(organization_id=organization_id)


@router.patch("/", response_model=TenantBrandingResponse)
def update_tenant_branding(payload: TenantBrandingUpdate, organization_id: str = Query("org-001")):
    """Update tenant brand colors, company logo, support contact, and domain."""
    return tenant_branding_service.update_branding(organization_id=organization_id, payload=payload)


@router.post("/verify-domain", response_model=DomainVerificationResult)
def verify_custom_domain(organization_id: str = Query("org-001")):
    """Perform CNAME DNS verification and TLS certificate provisioning."""
    return tenant_branding_service.verify_custom_domain(organization_id=organization_id)
