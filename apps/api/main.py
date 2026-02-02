"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.

    Args:
        app: FastAPI application instance.

    Yields:
        None during application runtime.
    """
    # Startup
    logger.info("Starting Credit Risk API...")
    logger.info(f"Environment: {'development' if app.debug else 'production'}")

    yield

    # Shutdown
    logger.info("Shutting down Credit Risk API...")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        settings: Application settings. If None, loads from environment.

    Returns:
        Configured FastAPI application instance.
    """
    if settings is None:
        settings = Settings()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Train and deploy credit risk models via REST API",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            Status message indicating API is healthy.
        """
        return {"status": "ok", "service": settings.app_name}

    # Include routers
    from apps.api.routers import auth, models, predict, train

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(train.router, prefix="/train", tags=["training"])
    app.include_router(predict.router, prefix="/predict", tags=["prediction"])
    app.include_router(models.router, prefix="/models", tags=["models"])

    return app


# Application instance for uvicorn
app = create_app()
