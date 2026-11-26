import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from fastapi import HTTPException, Request, Response, status
except ImportError:  # pragma: no cover - allows standalone unit tests without FastAPI
    HTTPException = Exception  # type: ignore
    Request = Any  # type: ignore
    Response = Any  # type: ignore
    status = None  # type: ignore


class RateLimiter:
    """
    Sliding-window / fixed-window hybrid rate limiter backed by Redis (INCR + EXPIRE)
    with automatic thread-safe in-memory fallback when Redis is unavailable.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._redis_client: Any = None
        self._redis_checked = False
        self._lock = threading.Lock()
        self._history: Dict[str, List[float]] = defaultdict(list)

    def _get_redis(self) -> Any:
        if self._redis_client is not None:
            return self._redis_client
        if self._redis_checked or not self.redis_url:
            return None
        self._redis_checked = True
        try:
            import redis

            client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            client.ping()
            self._redis_client = client
        except Exception:
            self._redis_client = None
        return self._redis_client

    def reset(self) -> None:
        """Clear in-memory sliding window state."""
        with self._lock:
            self._history.clear()

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """
        Evaluate whether `key` is allowed.
        Returns `(allowed, remaining, retry_after_seconds)`.
        """
        client = self._get_redis()
        if client is not None:
            try:
                redis_key = f"ratelimit:{key}"
                count = int(client.incr(redis_key))
                if count == 1:
                    client.expire(redis_key, window_seconds)
                if count > max_requests:
                    ttl = int(client.ttl(redis_key))
                    return False, 0, max(ttl, 1)
                return True, max(max_requests - count, 0), 0
            except Exception:
                pass

        now = time.time()
        window_start = now - window_seconds
        with self._lock:
            timestamps = [t for t in self._history[key] if t > window_start]
            if len(timestamps) >= max_requests:
                self._history[key] = timestamps
                retry_after = int(timestamps[0] + window_seconds - now)
                return False, 0, max(retry_after, 1)
            timestamps.append(now)
            self._history[key] = timestamps
            return True, max(max_requests - len(timestamps), 0), 0


class InMemoryRateLimiter:
    """Backward-compatible in-memory sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 15):
        self.limit = requests_per_minute
        self.window_seconds = 60
        self._limiter = RateLimiter(redis_url=None)

    def is_rate_limited(self, client_key: str) -> Tuple[bool, int]:
        allowed, _remaining, retry_after = self._limiter.check(
            f"legacy:{client_key}", self.limit, self.window_seconds
        )
        return (not allowed), retry_after


def _extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For") if hasattr(request, "headers") else None
    if forwarded:
        return forwarded.split(",")[0].strip()
    if getattr(request, "client", None) and getattr(request.client, "host", None):
        return request.client.host
    return "unknown"


try:
    from backend.app.core.config import settings

    _shared_limiter = RateLimiter(redis_url=settings.REDIS_URL)
except Exception:
    settings = None  # type: ignore
    _shared_limiter = RateLimiter(redis_url=None)


def rate_limit(scope: str, max_requests: int, window_seconds: int = 60) -> Callable:
    """FastAPI dependency enforcing scoped Redis/in-memory rate limits with headers."""

    async def _dependency(request: Request, response: Response) -> None:
        if settings is not None and not getattr(settings, "RATE_LIMIT_ENABLED", True):
            return
        client_ip = _extract_client_ip(request)
        allowed, remaining, retry_after = _shared_limiter.check(
            f"{scope}:{client_ip}", max_requests=max_requests, window_seconds=window_seconds
        )
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {scope}. Try again in {retry_after} seconds.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

    return _dependency


# Legacy shared dependency preserved for backwards compatibility
ai_rate_limiter = InMemoryRateLimiter(requests_per_minute=20)


async def check_ai_rate_limit(request: Request, response: Response) -> None:
    """FastAPI dependency checking AI inference request rate against client IP."""
    limit = getattr(settings, "RATE_LIMIT_AI_PER_MINUTE", 30) if settings else 20
    dep = rate_limit("ai_inference", max_requests=limit, window_seconds=60)
    await dep(request, response)
