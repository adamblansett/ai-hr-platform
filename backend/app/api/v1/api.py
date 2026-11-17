from fastapi import APIRouter
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.employees import router as employees_router
from backend.app.api.v1.endpoints.webhooks import router as webhooks_router
from backend.app.api.v1.endpoints.onboarding import router as onboarding_router
from backend.app.api.v1.endpoints.audit import router as audit_router
from backend.app.api.v1.endpoints.policies import router as policies_router
from backend.app.api.v1.endpoints.leave import router as leave_router
from backend.app.api.v1.endpoints.performance import router as performance_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(employees_router, prefix="/employees", tags=["Employee Directory & Profile"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["Employee Lifecycle & Onboarding"])
api_router.include_router(policies_router, prefix="/policies", tags=["Policy Enforcement & RAG"])
api_router.include_router(leave_router, prefix="/leave", tags=["Leave & Attendance Tracking"])
api_router.include_router(performance_router, prefix="/performance", tags=["Performance & 360 Reviews"])
api_router.include_router(audit_router, prefix="/audit-logs", tags=["Audit & Compliance"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Upstream Webhooks"])
