import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SSOProviderType(str, Enum):
    SAML_2_0 = "SAML_2_0"
    OIDC = "OIDC"


class SSOProviderConfig(Base):
    """Enterprise Identity Provider (Okta / Entra ID / Google Workspace) SSO configuration."""
    __tablename__ = "sso_provider_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_type: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    issuer_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sso_login_url: Mapped[str] = mapped_column(String(500), nullable=False)
    client_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    certificate_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    enforced_for_admins: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False)


class UserMFASetting(Base):
    """Per-employee RFC 6238 TOTP MFA enrollment and hashed backup codes."""
    __tablename__ = "user_mfa_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    totp_secret: Mapped[str] = mapped_column(String(128), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    backup_codes_hashed: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False)
