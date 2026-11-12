"""Authentication and CSRF dependencies protecting private routes."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.security import (
    ACCESS_TOKEN_COOKIE,
    CSRF_COOKIE,
    CSRF_HEADER,
    csrf_tokens_match,
    decode_access_token,
)
from app.logging.context import user_id_ctx
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ForbiddenError, UnauthorizedError

# auto_error=False: the token may come from the HttpOnly cookie instead of the header.
bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token (Swagger / API clients)")

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the Bearer header or the HttpOnly cookie.

    For cookie-based authentication on state-changing methods, the double-submit CSRF token is
    enforced: the ``X-CSRF-Token`` header must match the ``csrf_token`` cookie. Bearer tokens are
    not sent automatically by browsers, so they are not exposed to CSRF.
    """
    token: str | None = None
    from_cookie = False
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    elif cookie_token := request.cookies.get(ACCESS_TOKEN_COOKIE):
        token = cookie_token
        from_cookie = True

    if not token:
        raise UnauthorizedError("Authentication required")

    user_id = decode_access_token(token)
    if user_id is None:
        raise UnauthorizedError("Invalid or expired token")

    if (
        from_cookie
        and request.method not in SAFE_METHODS
        and not csrf_tokens_match(
            request.cookies.get(CSRF_COOKIE), request.headers.get(CSRF_HEADER)
        )
    ):
        raise ForbiddenError("Invalid or missing CSRF token")

    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("Invalid or expired token")

    user_id_ctx.set(str(user.id))
    request.state.user_id = str(user.id)
    return user
