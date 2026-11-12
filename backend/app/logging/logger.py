"""Logging configuration: every log line is emitted as a single JSON object on stdout."""

import logging
import sys

from app.config.settings import settings
from app.logging.formatters import JSONFormatter

APP_LOGGER_NAME = "app"


def configure_logging(level: str | None = None) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level or settings.LOG_LEVEL)

    # Route uvicorn logs through the JSON handler; access logs are replaced by our middleware.
    for name in ("uvicorn", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{APP_LOGGER_NAME}.{name}")
