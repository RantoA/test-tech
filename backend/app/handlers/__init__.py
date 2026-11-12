from fastapi import FastAPI

from app.handlers.client_error_handlers import register_client_error_handlers
from app.handlers.server_error_handlers import register_server_error_handlers


def register_exception_handlers(app: FastAPI) -> None:
    register_client_error_handlers(app)
    register_server_error_handlers(app)
