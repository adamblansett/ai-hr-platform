from fastapi import APIRouter
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.employees import router as employees_router
from backend.app.api.v1.endpoints.webhooks import router as webhooks_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(employees_router, prefix="/employees", tags=["Employee Directory & Profile"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Upstream Webhooks"])
