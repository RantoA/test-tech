"""Success (2xx) response helpers used by routes. Exceptions are NOT used for success paths."""

from typing import Any

from fastapi import Response, status
from fastapi.responses import JSONResponse

from app.utils.responses import json_response


def ok(data: Any = None, message: str = "OK") -> JSONResponse:
    return json_response(status.HTTP_200_OK, message, data)


def created(data: Any = None, message: str = "Created") -> JSONResponse:
    return json_response(status.HTTP_201_CREATED, message, data)


def no_content() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
