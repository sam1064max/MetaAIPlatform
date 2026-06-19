# ---------------------------------------------------------------------------
# MetaAI Platform - Backend Entrypoint
# FastAPI application with CORS, request logging, health checks, and router
# registration. Each API module is self-contained in api/v1/endpoints/.
# ---------------------------------------------------------------------------
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.api.v1.endpoints import (
    auth,
    agents,
    tools,
    evaluations,
    rag,
    governance,
    observability,
    dashboard,
)

# Logging: INFO level in development, WARNING in production to reduce noise
logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger("metaai")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    # Only expose interactive docs in development
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# -----------------------------------------------------------------------
# CORS: Allow all origins in development. Tighten in production.
# -----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------
# Request logging: Logs method, path, status, and duration for every call.
# -----------------------------------------------------------------------
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    elapsed = (time.monotonic() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


# -----------------------------------------------------------------------
# Health & root endpoints for load balancer and CI/CD verification.
# -----------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.VERSION}


# -----------------------------------------------------------------------
# Router registration: Each domain maps to a versioned prefix.
# -----------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["Tools"])
app.include_router(evaluations.router, prefix="/api/v1/evaluations", tags=["Evaluations"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(governance.router, prefix="/api/v1", tags=["Governance"])
app.include_router(observability.router, prefix="/api/v1", tags=["Observability"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])


@app.on_event("startup")
async def startup():
    from backend.db import init_db
    try:
        await init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning("Database init skipped (not ready yet): %s", e)


# -----------------------------------------------------------------------
# Global exception handler: Captures unhandled errors and returns 500.
# -----------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
