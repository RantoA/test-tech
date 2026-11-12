"""Handlers for server errors (5xx). Stack traces are logged, never returned to clients."""

import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, OperationalError

from app.config.settings import settings
from app.logging.logger import get_logger
from app.utils.responses import json_response

logger = get_logger("errors")


def _debug_data(exc: Exception) -> dict[str, object] | None:
    if settings.APP_ENV != "development":
        return None
    return {"error": type(exc).__name__, "trace": traceback.format_exception(exc)[-3:]}


def _is_connection_error(exc: DBAPIError) -> bool:
    return isinstance(exc, OperationalError) or bool(exc.connection_invalidated)


async def database_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    if _is_connection_error(exc):
        logger.critical("Database unavailable", exc_info=exc, extra={"status_code": 503})
        return json_response(503, "Service temporarily unavailable", _debug_data(exc))
    logger.error("Database error", exc_info=exc, extra={"status_code": 500})
    return json_response(500, "Internal server error", _debug_data(exc))


async def connection_error_handler(request: Request, exc: OSError) -> JSONResponse:
    logger.critical("Dependency unavailable", exc_info=exc, extra={"status_code": 503})
    return json_response(503, "Service temporarily unavailable", _debug_data(exc))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled server error", exc_info=exc, extra={"status_code": 500})
    return json_response(500, "Internal server error", _debug_data(exc))


def register_server_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DBAPIError, database_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConnectionRefusedError, connection_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
