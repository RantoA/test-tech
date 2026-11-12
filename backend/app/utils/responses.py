"""Builders for the uniform JSON envelope: {"status", "message", "data"}."""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def build_body(status_code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"status": status_code, "message": message, "data": jsonable_encoder(data)}


def json_response(
    status_code: int,
    message: str,
    data: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=build_body(status_code, message, data), headers=headers
    )
