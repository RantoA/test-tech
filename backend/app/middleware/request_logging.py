"""Pure ASGI middleware: assigns a request id, measures latency and logs every request."""

import time
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.logging.context import request_id_ctx, user_id_ctx
from app.logging.logger import get_logger

logger = get_logger("http")
REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope["headers"]).get(REQUEST_ID_HEADER.lower().encode())
        request_id = incoming.decode()[:64] if incoming else uuid.uuid4().hex
        rid_token = request_id_ctx.set(request_id)
        uid_token = user_id_ctx.set(None)
        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                message.setdefault("headers", [])
                message["headers"].append((REQUEST_ID_HEADER.encode(), request_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            # user_id is set by the auth dependency on request.state (shared through the scope).
            user_id = scope.get("state", {}).get("user_id")
            log = logger.info
            if status_code >= 500:
                log = logger.error
            elif status_code >= 400:
                log = logger.warning
            log(
                "Request completed",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": status_code,
                    "execution_time": elapsed_ms,
                    "user_id": user_id,
                },
            )
            request_id_ctx.reset(rid_token)
            user_id_ctx.reset(uid_token)
