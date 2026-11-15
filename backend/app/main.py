from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (e.g. database connect, model warm-up)
    yield
    # Shutdown actions

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "llm_provider": settings.PRIMARY_LLM_PROVIDER,
    }

# API V1 router placeholder
# app.include_router(api_router, prefix=settings.API_V1_STR)
