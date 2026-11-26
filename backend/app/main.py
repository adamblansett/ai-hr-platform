import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.logging import configure_logging, request_id_ctx
from backend.app.api.v1.api import api_router

configure_logging(level=settings.LOG_LEVEL, service_name=settings.PROJECT_NAME)
logger = logging.getLogger("ai_hr_platform.http")

# Prometheus Metrics Collectors
HTTP_REQUESTS_TOTAL = Counter(
    "ai_hr_http_requests_total",
    "Total HTTP requests processed by ai-hr-platform",
    ["method", "path", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "ai_hr_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
HTTP_REQUESTS_IN_FLIGHT = Gauge(
    "ai_hr_http_requests_in_flight",
    "Number of in-flight HTTP requests",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ai-hr-platform v2.1.0 API service")
    yield
    logger.info("Shutting down ai-hr-platform API service")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.1.0",
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
async def observability_and_correlation_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    token = request_id_ctx.set(request_id)
    start_time = time.time()
    HTTP_REQUESTS_IN_FLIGHT.inc()
    route_path = request.url.path
    method = request.method
    status_code = 500
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        duration_sec = time.time() - start_time
        duration_ms = duration_sec * 1000.0
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        HTTP_REQUESTS_TOTAL.labels(method=method, path=route_path, status_code=str(status_code)).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=route_path).observe(duration_sec)
        logger.info(
            "Request completed",
            extra={
                "method": method,
                "path": route_path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": request.client.host if request.client else "unknown",
            },
        )
        return response
    except Exception:
        duration_sec = time.time() - start_time
        HTTP_REQUESTS_TOTAL.labels(method=method, path=route_path, status_code="500").inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=route_path).observe(duration_sec)
        logger.exception("Unhandled exception during request", extra={"method": method, "path": route_path})
        raise
    finally:
        HTTP_REQUESTS_IN_FLIGHT.dec()
        request_id_ctx.reset(token)


@app.get("/health", tags=["Health & Telemetry"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "2.1.0",
        "llm_provider": settings.PRIMARY_LLM_PROVIDER,
    }


@app.get("/health/live", tags=["Health & Telemetry"], summary="Kubernetes liveness probe")
async def liveness_probe():
    return {"status": "alive", "service": settings.PROJECT_NAME, "version": "2.1.0"}


@app.get("/health/ready", tags=["Health & Telemetry"], summary="Kubernetes readiness probe (Postgres & Redis)")
async def readiness_probe():
    checks = {"postgres": "error", "redis": "error"}
    is_ready = True

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:
        logger.warning("Readiness postgres check failed: %s", exc)
        is_ready = False

    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0, socket_timeout=1.0)
        try:
            await r.ping()
            checks["redis"] = "ok"
        finally:
            await r.aclose()
    except Exception as exc:
        logger.warning("Readiness redis check failed: %s", exc)
        is_ready = False

    payload = {"status": "ready" if is_ready else "degraded", "checks": checks, "version": "2.1.0"}
    return JSONResponse(status_code=200 if is_ready else 503, content=payload)


@app.get("/metrics", tags=["Health & Telemetry"], summary="Prometheus exposition telemetry metrics")
async def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Mount API V1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
