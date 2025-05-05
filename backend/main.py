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

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger("metaai")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Request logging middleware ----
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


# ---- Root and health ----
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


# ---- Include routers ----
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["Tools"])
app.include_router(evaluations.router, prefix="/api/v1/evaluations", tags=["Evaluations"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(governance.router, prefix="/api/v1", tags=["Governance"])
app.include_router(observability.router, prefix="/api/v1", tags=["Observability"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
