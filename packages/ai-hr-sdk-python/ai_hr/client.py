import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


class AIHRClient:
    """Synchronous / standard library client for ai-hr-platform v2.1 API."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1", api_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.refresh_token_value: Optional[str] = None

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json", "User-Agent": "ai-hr-python-sdk/2.1.0"}
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

    # Authentication & Session Management
    def authenticate(self, email: str, password: str) -> str:
        """Authenticate user and store access + refresh tokens."""
        res = self._request("POST", "/auth/login", {"email": email, "password": password})
        self.api_token = res.get("access_token")
        self.refresh_token_value = res.get("refresh_token")
        return self.api_token

    def refresh_access_token(self, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        """Rotate refresh token and obtain fresh access/refresh tokens."""
        token = refresh_token or self.refresh_token_value
        if not token:
            raise ValueError("No refresh token available")
        res = self._request("POST", "/auth/refresh", {"refresh_token": token})
        self.api_token = res.get("access_token")
        self.refresh_token_value = res.get("refresh_token")
        return res

    def logout(self) -> Dict[str, Any]:
        """Revoke active access and refresh tokens and clear local session."""
        res = self._request("POST", "/auth/logout", {"refresh_token": self.refresh_token_value})
        self.api_token = None
        self.refresh_token_value = None
        return res

    def get_me(self) -> Dict[str, Any]:
        """Fetch current authenticated employee profile."""
        return self._request("GET", "/auth/me")

    # Core HR Directory, Onboarding & Leave
    def list_employees(self, page: int = 1, search: str = "") -> Dict[str, Any]:
        query = urllib.parse.urlencode({"page": page, "search": search})
        return self._request("GET", f"/employees?{query}")

    def get_onboarding_progress(self) -> Dict[str, Any]:
        return self._request("GET", "/onboarding/me/progress")

    def get_leave_balances(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/leave/balances/me")

    def submit_leave_request(self, policy_id: str, start_date: str, end_date: str, reason: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/leave/requests",
            {"policy_id": policy_id, "start_date": start_date, "end_date": end_date, "reason": reason},
        )

    # Policy RAG & Compensation
    def ask_policy(self, question: str, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Execute multilingual grounded policy RAG query."""
        payload: Dict[str, Any] = {"question": question}
        if category_filter:
            payload["category_filter"] = category_filter
        return self._request("POST", "/policies/chat", payload)

    def get_compensation(self) -> Dict[str, Any]:
        """Fetch employee salary, equity vesting, and paystub history."""
        return self._request("GET", "/compensation/me")

    def dispatch_outbound_ping(self, subscription_id: str) -> Dict[str, Any]:
        """Trigger test webhook ping with HMAC-SHA256 signature."""
        return self._request("POST", f"/webhooks/outbound/subscriptions/{subscription_id}/test-ping")

    # v2.0 Enterprise Intelligence & Global Ops
    def get_salary_benchmarks(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        q = f"?department={urllib.parse.quote(department)}" if department else ""
        return self._request("GET", f"/benchmarking/{q}")

    def list_immigration_cases(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        q = f"?employee_id={urllib.parse.quote(employee_id)}" if employee_id else ""
        return self._request("GET", f"/immigration/cases{q}")

    def get_tenant_branding(self, organization_id: str = "org-001") -> Dict[str, Any]:
        return self._request("GET", f"/branding/?organization_id={urllib.parse.quote(organization_id)}")

    # v2.1 Enterprise SSO & MFA
    def list_sso_providers(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/security/sso/providers")

    def get_oidc_authorize_url(self, provider_id: Optional[str] = None) -> Dict[str, Any]:
        q = f"?provider_id={urllib.parse.quote(provider_id)}" if provider_id else ""
        return self._request("GET", f"/security/sso/oidc/authorize{q}")

    def setup_mfa(self, employee_id: str = "emp-001", email: str = "elena.rostova@acme.corp") -> Dict[str, Any]:
        q = urllib.parse.urlencode({"employee_id": employee_id, "email": email})
        return self._request("POST", f"/security/mfa/setup?{q}")

    def verify_mfa(self, employee_id: str, code: str) -> Dict[str, Any]:
        return self._request("POST", "/security/mfa/verify", {"employee_id": employee_id, "code": code})

    # v2.1 Notifications & Digests
    def list_notifications(self, recipient_id: str = "emp-001", unread_only: bool = False) -> List[Dict[str, Any]]:
        q = urllib.parse.urlencode({"recipient_id": recipient_id, "unread_only": str(unread_only).lower()})
        return self._request("GET", f"/notifications/me?{q}")

    def trigger_daily_digest(self, organization_id: str = "org-001") -> Dict[str, Any]:
        return self._request("POST", f"/notifications/digest/trigger?organization_id={urllib.parse.quote(organization_id)}")

    # v2.1 Workforce Planning & Headcount Forecasting
    def list_workforce_plans(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/workforce-planning/plans")

    def simulate_workforce_plan(self, plan_id: str, scenario: str = "BASELINE", avg_base_salary: float = 175000.0) -> Dict[str, Any]:
        return self._request(
            "POST",
            f"/workforce-planning/plans/{plan_id}/simulate",
            {"scenario": scenario, "avg_base_salary": avg_base_salary},
        )

    def sync_requisition_to_recruiter(self, req_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/workforce-planning/requisitions/{req_id}/sync-recruiter")
