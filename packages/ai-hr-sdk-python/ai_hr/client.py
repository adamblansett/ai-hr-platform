import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class AIHRClient:
    """Synchronous / standard library client for ai-hr-platform API."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1", api_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json", "User-Agent": "ai-hr-python-sdk/1.0.0"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode("utf-8")
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"API Error {e.code}: {err_body}")

    def authenticate(self, email: str, password: str) -> str:
        """Authenticate user and store access token."""
        res = self._request("POST", "/auth/login", {"email": email, "password": password})
        self.api_token = res.get("access_token")
        return self.api_token

    def get_me(self) -> Dict[str, Any]:
        """Fetch current authenticated employee profile."""
        return self._request("GET", "/auth/me")

    def ask_policy(self, question: str, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Execute multilingual grounded policy RAG query."""
        payload = {"question": question}
        if category_filter:
            payload["category_filter"] = category_filter
        return self._request("POST", "/policies/chat", payload)

    def get_compensation(self) -> Dict[str, Any]:
        """Fetch employee salary, equity vesting, and paystub history."""
        return self._request("GET", "/compensation/me")

    def dispatch_outbound_ping(self, subscription_id: str) -> Dict[str, Any]:
        """Trigger test webhook ping with HMAC-SHA256 signature."""
        return self._request("POST", f"/webhooks/outbound/subscriptions/{subscription_id}/test-ping")
