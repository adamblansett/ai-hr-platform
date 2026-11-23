import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any],
    organization_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "nbf": now,
        "iat": now,
        "jti": uuid.uuid4().hex,
        "sub": str(subject),
        "org_id": str(organization_id),
        "role": str(role),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    organization_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7) # 7-day refresh token
    
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "nbf": now,
        "iat": now,
        "jti": uuid.uuid4().hex,
        "sub": str(subject),
        "org_id": str(organization_id),
        "role": str(role),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

REVOKED_JTIS: set[str] = set()

def revoke_token_jti(jti: str) -> None:
    """Revoke a specific JWT jti (token ID) on logout or security intervention."""
    REVOKED_JTIS.add(jti)

def is_jti_revoked(jti: str) -> bool:
    """Check if a JWT has been revoked."""
    return jti in REVOKED_JTIS

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True, "verify_nbf": True, "verify_iat": True}
        )
        jti = payload.get("jti")
        if jti and is_jti_revoked(jti):
            return None
        return payload
    except JWTError:
        return None
