import base64
import hashlib
import hmac
import secrets
import struct
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.app.core.security import create_access_token
from backend.app.schemas.sso_mfa import (
    MFASetupResponse,
    MFAStatusResponse,
    OIDCAuthorizeResponse,
    SAMLCallbackResponse,
    SSOProviderCreate,
    SSOProviderResponse,
)


def generate_totp_secret(length_bytes: int = 20) -> str:
    """Generate a base32-encoded RFC 6238 shared secret (no padding)."""
    return base64.b32encode(secrets.token_bytes(length_bytes)).decode("ascii").rstrip("=")


def generate_totp_code(
    secret: str,
    timestamp: Optional[float] = None,
    interval: int = 30,
    digits: int = 6,
) -> str:
    """Compute RFC 6238 TOTP code using HMAC-SHA1."""
    normalized = secret.strip().upper().replace(" ", "")
    padding = (-len(normalized)) % 8
    key = base64.b32decode(normalized + ("=" * padding), casefold=True)
    counter = int((timestamp if timestamp is not None else time.time()) // interval)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code_int % (10**digits)).zfill(digits)


def verify_totp_code(
    secret: str,
    code: str,
    timestamp: Optional[float] = None,
    window: int = 1,
    interval: int = 30,
) -> bool:
    """Verify a 6-digit TOTP code across [-window, +window] intervals in constant time."""
    clean_code = code.strip()
    if not clean_code.isdigit() or len(clean_code) != 6:
        return False
    now = timestamp if timestamp is not None else time.time()
    for step in range(-window, window + 1):
        expected = generate_totp_code(secret, timestamp=now + (step * interval), interval=interval)
        if hmac.compare_digest(expected, clean_code):
            return True
    return False


def build_otpauth_uri(email: str, secret: str, issuer: str = "ai-hr-platform") -> str:
    label = urllib.parse.quote(f"{issuer}:{email}")
    issuer_param = urllib.parse.quote(issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_param}&algorithm=SHA1&digits=6&period=30"


def generate_backup_codes(count: int = 8) -> List[str]:
    """Generate human-readable one-time backup recovery codes."""
    return [f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}" for _ in range(count)]


def hash_backup_code(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()


def generate_pkce_challenge() -> Tuple[str, str]:
    """Return `(code_verifier, S256 code_challenge)` per RFC 7636."""
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def parse_saml_assertion(saml_response_b64: str) -> Dict[str, str]:
    """
    Safely parse a Base64-encoded SAML 2.0 XML Response using defusedxml (XXE-safe).
    Extracts NameID email, Issuer, and Assertion ID.
    """
    import defusedxml.ElementTree as SafeET

    try:
        raw_xml = base64.b64decode(saml_response_b64, validate=True).decode("utf-8")
    except Exception as exc:
        raise ValueError(f"Invalid Base64 SAML payload: {exc}") from exc

    try:
        root = SafeET.fromstring(raw_xml)
    except Exception as exc:
        raise ValueError(f"Malformed SAML XML assertion: {exc}") from exc

    email = ""
    issuer = ""
    assertion_id = ""

    for elem in root.iter():
        local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if local_name == "NameID" and elem.text:
            email = elem.text.strip()
        elif local_name == "Issuer" and elem.text and not issuer:
            issuer = elem.text.strip()
        elif local_name == "Assertion" and not assertion_id:
            assertion_id = elem.attrib.get("ID", f"assertion-{uuid.uuid4().hex[:12]}")

    if not email:
        raise ValueError("SAML assertion missing NameID subject email")

    return {
        "email": email,
        "issuer": issuer or "https://idp.enterprise.local",
        "assertion_id": assertion_id or f"assertion-{uuid.uuid4().hex[:12]}",
    }


class SSOMFAService:
    def __init__(self):
        self._providers: Dict[str, dict] = {}
        self._mfa_records: Dict[str, dict] = {}
        self._seed_defaults()

    def _seed_defaults(self):
        now = datetime.now(timezone.utc)
        p1 = {
            "id": "sso-okta-oidc-01",
            "organization_id": "org-001",
            "provider_type": "OIDC",
            "provider_name": "Okta Workforce Identity (OIDC)",
            "issuer_url": "https://acme.okta.com/oauth2/default",
            "sso_login_url": "https://acme.okta.com/oauth2/default/v1/authorize",
            "client_id": "0oa9aihrplatformoidc",
            "certificate_fingerprint": None,
            "enforced_for_admins": True,
            "is_active": True,
            "created_at": now,
        }
        p2 = {
            "id": "sso-entra-saml-02",
            "organization_id": "org-001",
            "provider_type": "SAML_2_0",
            "provider_name": "Microsoft Entra ID (SAML 2.0)",
            "issuer_url": "https://sts.windows.net/99887766-5544-3322-1100-aabbccddeeff/",
            "sso_login_url": "https://login.microsoftonline.com/99887766/saml2",
            "client_id": None,
            "certificate_fingerprint": "SHA256:9F:3B:77:C1:42:AA:08:E3:11:44:8D:00:55:B2:9E:1A",
            "enforced_for_admins": True,
            "is_active": True,
            "created_at": now,
        }
        self._providers[p1["id"]] = p1
        self._providers[p2["id"]] = p2

        sample_secret = "JBSWY3DPEHPK3PXP"
        sample_codes = ["A1B2-C3D4", "E5F6-G7H8", "J9K0-L1M2", "N3P4-Q5R6"]
        self._mfa_records["emp-001"] = {
            "employee_id": "emp-001",
            "secret": sample_secret,
            "is_enabled": True,
            "backup_codes_hashed": [hash_backup_code(c) for c in sample_codes],
            "last_verified_at": now,
        }

    def list_providers(self) -> List[SSOProviderResponse]:
        return [SSOProviderResponse(**p) for p in self._providers.values()]

    def create_provider(self, payload: SSOProviderCreate, organization_id: str = "org-001") -> SSOProviderResponse:
        pid = f"sso-{uuid.uuid4().hex[:10]}"
        record = {
            "id": pid,
            "organization_id": organization_id,
            "provider_type": payload.provider_type,
            "provider_name": payload.provider_name,
            "issuer_url": payload.issuer_url,
            "sso_login_url": payload.sso_login_url,
            "client_id": payload.client_id,
            "certificate_fingerprint": payload.certificate_fingerprint,
            "enforced_for_admins": payload.enforced_for_admins,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        self._providers[pid] = record
        return SSOProviderResponse(**record)

    def build_oidc_authorize(
        self,
        provider_id: Optional[str] = None,
        redirect_uri: str = "http://localhost:5173/sso/callback",
    ) -> OIDCAuthorizeResponse:
        provider = None
        if provider_id and provider_id in self._providers:
            provider = self._providers[provider_id]
        else:
            provider = next((p for p in self._providers.values() if p["provider_type"] == "OIDC"), None)
        if not provider:
            raise ValueError("No OIDC provider configured")

        state = secrets.token_urlsafe(24)
        _verifier, code_challenge = generate_pkce_challenge()
        params = urllib.parse.urlencode(
            {
                "client_id": provider.get("client_id") or "ai-hr-client",
                "response_type": "code",
                "scope": "openid profile email",
                "redirect_uri": redirect_uri,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )
        return OIDCAuthorizeResponse(
            provider_id=provider["id"],
            authorization_url=f"{provider['sso_login_url']}?{params}",
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )

    def handle_saml_callback(self, provider_id: str, saml_response_b64: str) -> SAMLCallbackResponse:
        if provider_id not in self._providers:
            raise ValueError(f"Unknown SSO provider: {provider_id}")
        parsed = parse_saml_assertion(saml_response_b64)
        token = create_access_token(
            subject=parsed["email"],
            organization_id=self._providers[provider_id]["organization_id"],
            role="EMPLOYEE",
        )
        return SAMLCallbackResponse(
            verified=True,
            email=parsed["email"],
            issuer=parsed["issuer"],
            assertion_id=parsed["assertion_id"],
            session_token=token,
        )

    def get_mfa_status(self, employee_id: str = "emp-001") -> MFAStatusResponse:
        rec = self._mfa_records.get(employee_id)
        if not rec:
            return MFAStatusResponse(
                employee_id=employee_id,
                is_enabled=False,
                enforced_by_policy=True,
                backup_codes_remaining=0,
                last_verified_at=None,
            )
        return MFAStatusResponse(
            employee_id=employee_id,
            is_enabled=rec["is_enabled"],
            enforced_by_policy=True,
            backup_codes_remaining=len(rec["backup_codes_hashed"]),
            last_verified_at=rec["last_verified_at"],
        )

    def setup_mfa(self, employee_id: str = "emp-001", email: str = "elena.rostova@acme.corp") -> MFASetupResponse:
        secret = generate_totp_secret()
        codes = generate_backup_codes(8)
        self._mfa_records[employee_id] = {
            "employee_id": employee_id,
            "secret": secret,
            "is_enabled": False,
            "backup_codes_hashed": [hash_backup_code(c) for c in codes],
            "last_verified_at": None,
        }
        return MFASetupResponse(
            employee_id=employee_id,
            secret=secret,
            otpauth_uri=build_otpauth_uri(email=email, secret=secret),
            backup_codes=codes,
            is_enabled=False,
        )

    def verify_mfa(self, employee_id: str, code: str) -> MFAStatusResponse:
        rec = self._mfa_records.get(employee_id)
        if not rec:
            raise ValueError("MFA has not been initialized for employee")

        verified = verify_totp_code(rec["secret"], code)
        if not verified:
            code_digest = hash_backup_code(code)
            if code_digest in rec["backup_codes_hashed"]:
                rec["backup_codes_hashed"].remove(code_digest)
                verified = True

        if not verified:
            raise ValueError("Invalid TOTP verification code or backup code")

        rec["is_enabled"] = True
        rec["last_verified_at"] = datetime.now(timezone.utc)
        return self.get_mfa_status(employee_id)

    def disable_mfa(self, employee_id: str = "emp-001") -> MFAStatusResponse:
        rec = self._mfa_records.get(employee_id)
        if rec:
            rec["is_enabled"] = False
            rec["backup_codes_hashed"] = []
        return self.get_mfa_status(employee_id)


sso_mfa_service = SSOMFAService()
