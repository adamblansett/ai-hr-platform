import time
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict

class InMemoryRateLimiter:
    """
    Sliding window rate limiter for protecting compute/inference intensive endpoints.
    Tracks client requests by IP address or Bearer token subject.
    """

    def __init__(self, requests_per_minute: int = 15):
        self.limit = requests_per_minute
        self.window_seconds = 60
        self._history: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, client_key: str) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - self.window_seconds

        # Filter out expired timestamps
        self._history[client_key] = [t for t in self._history[client_key] if t > window_start]

        if len(self._history[client_key]) >= self.limit:
            retry_after = int(self._history[client_key][0] + self.window_seconds - now)
            return True, max(retry_after, 1)

        self._history[client_key].append(now)
        return False, 0

# Rate limiter instances for inference routes
ai_rate_limiter = InMemoryRateLimiter(requests_per_minute=20)

async def check_ai_rate_limit(request: Request):
    """
    FastAPI dependency checking request rate against client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    is_limited, retry_after = ai_rate_limiter.is_rate_limited(client_ip)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for AI inference. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
