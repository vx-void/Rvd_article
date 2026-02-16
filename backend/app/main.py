"""FastAPI application entry point."""

import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from backend.app.api.v1.router import api_router
from backend.app.config import get_settings
from backend.app.exceptions import AuthenticationError, RateLimitExceeded
from backend.app.logging_config import get_logger, setup_logging
from backend.app.services.metrics import MetricsService

# Setup logging first
settings = get_settings()
setup_logging(settings.log_level, json_format=settings.log_format == "json")
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production RAG API for hydraulic components search",
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Middleware: Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware: Request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
        client=request.client.host if request.client else None,
    )

    # Add rate limit headers
    if hasattr(request.state, "rate_limit"):
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit.get("reset", 0))

    return response


# Exception handlers
@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "authentication_error"},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "rate_limit_exceeded"},
        headers=exc.headers,
    )


# Include routers
app.include_router(api_router)

# Metrics endpoint
metrics_service = MetricsService()


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    content, content_type = metrics_service.get_prometheus_metrics()
    return Response(content=content, media_type=content_type)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(
        "application_startup",
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize RAG service (loads models)
    from backend.app.dependencies import get_rag_service
    get_rag_service()

    logger.info("application_ready")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("application_shutdown")


# Root endpoint
@app.get("/")
async def root():
    """API root."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None,
    }