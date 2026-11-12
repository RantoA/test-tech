"""Handlers for client errors (4xx): domain errors, HTTP exceptions and validation errors."""

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging.logger import get_logger
from app.utils.exceptions import AppError
from app.utils.responses import json_response

logger = get_logger("errors")

_SENSITIVE_FIELDS = {"password", "new_password", "current_password"}


def _format_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted = []
    for error in errors:
        loc = [str(part) for part in error.get("loc", ()) if part not in ("body", "query", "path")]
        message = str(error.get("msg", "Invalid value")).removeprefix("Value error, ")
        formatted.append(
            {"field": ".".join(loc) or None, "message": message, "type": error.get("type")}
        )
    return formatted


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    level = logger.error if exc.status_code >= 500 else logger.warning
    level(exc.message, extra={"status_code": exc.status_code, "path": request.url.path})
    return json_response(exc.status_code, exc.message, exc.data)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
    logger.warning(
        "HTTP error",
        extra={"status_code": exc.status_code, "path": request.url.path, "detail": message},
    )
    return json_response(exc.status_code, message, None, headers=getattr(exc, "headers", None))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = _format_validation_errors(list(exc.errors()))
    logger.warning(
        "Validation error",
        extra={
            "status_code": 422,
            "path": request.url.path,
            # Never log submitted values: they may contain passwords.
            "fields": [e["field"] for e in errors if e["field"] not in _SENSITIVE_FIELDS] or None,
        },
    )
    return json_response(422, "Validation error", {"errors": errors})


def register_client_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
