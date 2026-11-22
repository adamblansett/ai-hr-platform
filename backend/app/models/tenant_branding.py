from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class SSLCertStatus(str, Enum):
    PENDING = "PENDING"
    ISSUED = "ISSUED"
    RENEWING = "RENEWING"
    EXPIRED = "EXPIRED"


class TenantBrandingConfig(Base):
    __tablename__ = "tenant_branding_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), default="Acme Corporation")
    custom_domain: Mapped[str] = mapped_column(String(150), default="people.internal.acme.corp")
    custom_domain_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    ssl_cert_status: Mapped[str] = mapped_column(String(30), default=SSLCertStatus.ISSUED.value)
    
    # Visual Theme & Brand Palette
    primary_color_hex: Mapped[str] = mapped_column(String(10), default="#4F46E5")  # Indigo-600
    secondary_color_hex: Mapped[str] = mapped_column(String(10), default="#10B981") # Emerald-500
    logo_url: Mapped[str] = mapped_column(String(255), default="https://cdn.enterprise.local/assets/logo.svg")
    favicon_url: Mapped[str] = mapped_column(String(255), default="https://cdn.enterprise.local/assets/favicon.ico")
    support_email: Mapped[str] = mapped_column(String(100), default="hr-support@acme.corp")
    portal_title: Mapped[str] = mapped_column(String(100), default="Acme Global People Platform")
    
    # KMS Tenant Isolation Key
    kms_key_id: Mapped[str] = mapped_column(String(100), default="arn:aws:kms:us-west-2:112233445566:key/mrk-tenant-acme-01")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
