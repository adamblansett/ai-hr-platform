from fastapi import APIRouter
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.employees import router as employees_router
from backend.app.api.v1.endpoints.webhooks import router as webhooks_router
from backend.app.api.v1.endpoints.onboarding import router as onboarding_router
from backend.app.api.v1.endpoints.audit import router as audit_router
from backend.app.api.v1.endpoints.policies import router as policies_router
from backend.app.api.v1.endpoints.leave import router as leave_router
from backend.app.api.v1.endpoints.performance import router as performance_router
from backend.app.api.v1.endpoints.integrations import router as integrations_router
from backend.app.api.v1.endpoints.scim_server import router as scim_router
from backend.app.api.v1.endpoints.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(employees_router, prefix="/employees", tags=["Employee Directory & Profile"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["Employee Lifecycle & Onboarding"])
api_router.include_router(policies_router, prefix="/policies", tags=["Policy Enforcement & RAG"])
api_router.include_router(leave_router, prefix="/leave", tags=["Leave & Attendance Tracking"])
api_router.include_router(performance_router, prefix="/performance", tags=["Performance & 360 Reviews"])
api_router.include_router(audit_router, prefix="/audit-logs", tags=["Audit & Compliance"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Upstream Webhooks"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["Chatbot & Webhook Integrations (Slack/Teams)"])
api_router.include_router(scim_router, prefix="/scim/v2", tags=["SCIM 2.0 Inbound Protocol"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["HR Analytics & Calibration"])
