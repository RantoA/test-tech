"""FastAPI application factory and entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config.database import engine
from app.config.security import CSRF_HEADER
from app.config.settings import settings
from app.handlers import register_exception_handlers
from app.handlers.success_handlers import ok
from app.logging.logger import configure_logging, get_logger
from app.middleware.request_logging import REQUEST_ID_HEADER, RequestLoggingMiddleware
from app.routes import auth, posts, uploads, users
from app.utils.responses import json_response

API_PREFIX = "/api/v1"
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Application started", extra={"env": settings.APP_ENV})
    yield
    await engine.dispose()
    logger.info("Application stopped")


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Blog Post Manager API — authentication, profile management, "
        "post CRUD with cover images. Every response uses the envelope "
        "`{status, message, data}`.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", CSRF_HEADER, REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    for router in (auth.router, users.router, posts.router):
        app.include_router(router, prefix=API_PREFIX)
    app.include_router(uploads.router)

    @app.get("/health", tags=["Health"], summary="Liveness and database check")
    async def health() -> JSONResponse:
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            logger.critical("Health check failed: database unreachable")
            return json_response(503, "Service temporarily unavailable", {"database": "down"})
        return ok({"database": "up"}, "Service healthy")

    return app


app = create_app()
