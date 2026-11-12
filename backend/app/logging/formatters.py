"""JSON log formatter enriched with request context."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.logging.context import request_id_ctx, user_id_ctx

# Attributes present on every LogRecord that must not be duplicated in the output.
_RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "color_message"}
_SENSITIVE_KEYS = {
    "password",
    "new_password",
    "current_password",
    "token",
    "access_token",
    "authorization",
    "cookie",
    "secret",
    "csrf_token",
}


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
        }
        for key, value in vars(record).items():
            if key in _RESERVED or key.startswith("_"):
                continue
            log[key] = "***" if key.lower() in _SENSITIVE_KEYS else value
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps({k: v for k, v in log.items() if v is not None}, default=str)
