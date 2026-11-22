import uuid
from datetime import datetime
from typing import Dict, Optional
from backend.app.schemas.tenant_branding import (
    TenantBrandingUpdate,
    TenantBrandingResponse,
    DomainVerificationResult,
)


class TenantBrandingService:
    def __init__(self):
        self._configs: Dict[str, dict] = {}
        self._seed_default_config()

    def _seed_default_config(self):
        org_id = "org-001"
        self._configs[org_id] = {
            "id": "brand-cfg-001",
            "organization_id": org_id,
            "company_name": "Acme Global Technologies",
            "custom_domain": "people.acme.corp",
            "custom_domain_verified": True,
            "ssl_cert_status": "ISSUED",
            "primary_color_hex": "#4F46E5",
            "secondary_color_hex": "#10B981",
            "logo_url": "https://cdn.enterprise.local/assets/acme-logo.svg",
            "favicon_url": "https://cdn.enterprise.local/assets/acme-favicon.ico",
            "support_email": "hr-operations@acme.corp",
            "portal_title": "Acme People & Culture Portal",
            "kms_key_id": "arn:aws:kms:us-west-2:112233445566:key/mrk-acme-prod-01",
            "updated_at": datetime.utcnow(),
        }

    def get_branding(self, organization_id: str = "org-001") -> TenantBrandingResponse:
        cfg = self._configs.get(organization_id)
        if not cfg:
            # Create default for new org
            cfg_id = f"brand-cfg-{uuid.uuid4().hex[:6]}"
            cfg = {
                "id": cfg_id,
                "organization_id": organization_id,
                "company_name": "Enterprise Organization",
                "custom_domain": f"hr.{organization_id}.enterprise.local",
                "custom_domain_verified": False,
                "ssl_cert_status": "PENDING",
                "primary_color_hex": "#4F46E5",
                "secondary_color_hex": "#10B981",
                "logo_url": "https://cdn.enterprise.local/assets/default-logo.svg",
                "favicon_url": "https://cdn.enterprise.local/assets/favicon.ico",
                "support_email": "support@enterprise.local",
                "portal_title": "Employee Operations Microservice",
                "kms_key_id": f"arn:aws:kms:us-west-2:112233445566:key/mrk-{organization_id}",
                "updated_at": datetime.utcnow(),
            }
            self._configs[organization_id] = cfg
        return TenantBrandingResponse(**cfg)

    def update_branding(self, organization_id: str, payload: TenantBrandingUpdate) -> TenantBrandingResponse:
        cfg = self.get_branding(organization_id)
        raw = self._configs[organization_id]

        if payload.company_name is not None:
            raw["company_name"] = payload.company_name
        if payload.custom_domain is not None:
            raw["custom_domain"] = payload.custom_domain
            raw["custom_domain_verified"] = False
            raw["ssl_cert_status"] = "PENDING"
        if payload.primary_color_hex is not None:
            raw["primary_color_hex"] = payload.primary_color_hex
        if payload.secondary_color_hex is not None:
            raw["secondary_color_hex"] = payload.secondary_color_hex
        if payload.logo_url is not None:
            raw["logo_url"] = payload.logo_url
        if payload.favicon_url is not None:
            raw["favicon_url"] = payload.favicon_url
        if payload.support_email is not None:
            raw["support_email"] = payload.support_email
        if payload.portal_title is not None:
            raw["portal_title"] = payload.portal_title

        raw["updated_at"] = datetime.utcnow()
        return TenantBrandingResponse(**raw)

    def verify_custom_domain(self, organization_id: str) -> DomainVerificationResult:
        cfg = self.get_branding(organization_id)
        raw = self._configs[organization_id]

        # Simulate DNS resolution & Let's Encrypt TLS handshake
        raw["custom_domain_verified"] = True
        raw["ssl_cert_status"] = "ISSUED"
        raw["updated_at"] = datetime.utcnow()

        return DomainVerificationResult(
            custom_domain=raw["custom_domain"],
            dns_cname_target="ingress.global.ai-hr-platform.cloud",
            dns_txt_verification_record=f"ai-hr-verify={uuid.uuid4().hex[:16]}",
            is_verified=True,
            ssl_cert_status="ISSUED",
            message=f"Custom domain {raw['custom_domain']} successfully verified via CNAME ingress! TLS certificate active.",
        )


tenant_branding_service = TenantBrandingService()
