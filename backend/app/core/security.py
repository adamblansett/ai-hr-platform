import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Thread-safe in-memory TTL revocation store used as fallback when Redis is unavailable
_REVOCATION_LOCK = threading.Lock()
_LOCAL_REVOKED_JTIS: Dict[str, float] = {}
REVOKED_JTIS: set[str] = set()
_REDIS_REVOCATION_PREFIX = "revoked_jti:"
_redis_client: Any = None
_redis_init_attempted = False


def _get_redis_client() -> Any:
    global _redis_client, _redis_init_attempted
    if _redis_client is not None:
        return _redis_client
    if _redis_init_attempted:
        return None
    _redis_init_attempted = True
    try:
        import redis

        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        client.ping()
        _redis_client = client
    except Exception:
        _redis_client = None
    return _redis_client


def reset_revocation_cache_for_tests() -> None:
    """Reset in-memory revocation registry for deterministic unit testing."""
    with _REVOCATION_LOCK:
        _LOCAL_REVOKED_JTIS.clear()
        REVOKED_JTIS.clear()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    organization_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "exp": expire,
        "nbf": now - timedelta(seconds=10),  # Leeway buffer prevents clock skew rejection
        "iat": now,
        "jti": uuid.uuid4().hex,
        "sub": str(subject),
        "org_id": str(organization_id),
        "role": str(role),
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    organization_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)  # 7-day refresh token

    to_encode: Dict[str, Any] = {
        "exp": expire,
        "nbf": now - timedelta(seconds=10),  # Leeway buffer prevents clock skew rejection
        "iat": now,
        "jti": uuid.uuid4().hex,
        "sub": str(subject),
        "org_id": str(organization_id),
        "role": str(role),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def calculate_remaining_ttl(payload: Dict[str, Any], default_ttl: int = 86400) -> int:
    """Compute remaining lifetime in seconds from a decoded JWT exp claim."""
    exp = payload.get("exp")
    if isinstance(exp, (int, float)):
        remaining = int(exp - time.time())
        return max(remaining, 1)
    return default_ttl


def revoke_token_jti(jti: str, ttl_seconds: int = 86400) -> None:
    """Revoke a JWT jti in Redis (with TTL) and in-memory fallback store."""
    if not jti:
        return
    ttl = max(int(ttl_seconds), 1)
    expires_at = time.time() + ttl
    with _REVOCATION_LOCK:
        _LOCAL_REVOKED_JTIS[jti] = expires_at
        REVOKED_JTIS.add(jti)

    client = _get_redis_client()
    if client is not None:
        try:
            client.setex(f"{_REDIS_REVOCATION_PREFIX}{jti}", ttl, "1")
        except Exception:
            pass


def is_jti_revoked(jti: str) -> bool:
    """Check Redis and in-memory TTL store for a revoked JWT jti."""
    if not jti:
        return False
    now = time.time()
    with _REVOCATION_LOCK:
        if jti in _LOCAL_REVOKED_JTIS:
            if _LOCAL_REVOKED_JTIS[jti] > now:
                return True
            _LOCAL_REVOKED_JTIS.pop(jti, None)
            REVOKED_JTIS.discard(jti)
        elif jti in REVOKED_JTIS:
            return True

    client = _get_redis_client()
    if client is not None:
        try:
            return bool(client.exists(f"{_REDIS_REVOCATION_PREFIX}{jti}"))
        except Exception:
            pass
    return False


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True, "verify_nbf": True, "verify_iat": True},
        )
        jti = payload.get("jti")
        if jti and is_jti_revoked(jti):
            return None
        return payload
    except JWTError:
        return None
