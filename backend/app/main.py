import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings
from backend.app.api.v1.api import api_router

# In-memory metrics counters
REQUEST_COUNT = 0
TOTAL_LATENCY_MS = 0.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
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

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    if settings.ENABLE_SECURITY_HEADERS:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
    return response

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    global REQUEST_COUNT, TOTAL_LATENCY_MS
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000.0

    REQUEST_COUNT += 1
    TOTAL_LATENCY_MS += duration_ms

    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
    return response

@app.get("/health", tags=["Health & Telemetry"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "llm_provider": settings.PRIMARY_LLM_PROVIDER,
    }

@app.get("/metrics", tags=["Health & Telemetry"], summary="Prometheus telemetry metrics")
async def get_metrics():
    avg_latency = (TOTAL_LATENCY_MS / REQUEST_COUNT) if REQUEST_COUNT > 0 else 0.0
    return {
        "http_requests_total": REQUEST_COUNT,
        "http_average_latency_ms": round(avg_latency, 2),
        "service": settings.PROJECT_NAME,
        "llm_primary_provider": settings.PRIMARY_LLM_PROVIDER,
        "llm_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL
    }

# Mount API V1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
