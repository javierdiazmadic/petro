"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from petro.core import get_logger, setup_logging
from petro.core.config import settings
from petro.core.exceptions import PetroException
from petro.core.security import setup_cors
from petro.api.routes import router as api_router
from petro.api.dashboard import router as dashboard_router
from petro.api.toledo_analysis import router as toledo_router
from petro.api.predictions import router as predictions_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # Setup logging
    setup_logging(level=settings.logging.level, format=settings.logging.format)

    # Create app
    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description=settings.api.description,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Setup CORS
    setup_cors(app, origins=settings.api.cors_origins)

    # Setup Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics/prometheus")

    # Include API routes
    app.include_router(api_router)
    app.include_router(dashboard_router)
    app.include_router(toledo_router)
    app.include_router(predictions_router)

    # Exception handlers
    @app.exception_handler(PetroException)
    async def petro_exception_handler(request: Request, exc: PetroException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )

    # Health check endpoint
    @app.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "version": settings.api.version,
            "environment": settings.env,
        }

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "name": settings.api.title,
            "version": settings.api.version,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "health_url": "/api/v1/health",
        }

    logger.info(f"FastAPI application created: {settings.api.title} v{settings.api.version}")

    return app


app = create_app()
