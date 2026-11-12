"""Authentication endpoints: register, login, logout."""

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from app.config.security import ACCESS_TOKEN_COOKIE, CSRF_COOKIE, generate_csrf_token
from app.config.settings import settings
from app.handlers.success_handlers import created, ok
from app.models.user import User
from app.schemas.auth import AuthPayload, LoginRequest
from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

_ERRORS = {
    401: {"description": "Invalid credentials"},
    409: {"description": "Email already used"},
    422: {"description": "Validation error"},
}


def _set_auth_cookies(response: Response, token: str) -> None:
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    common = {
        "max_age": max_age,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
        "path": "/",
    }
    response.set_cookie(ACCESS_TOKEN_COOKIE, token, httponly=True, **common)
    # Readable by the frontend so it can echo it in the X-CSRF-Token header (double submit).
    response.set_cookie(CSRF_COOKIE, generate_csrf_token(), httponly=False, **common)


def _clear_auth_cookies(response: Response) -> None:
    for name in (ACCESS_TOKEN_COOKIE, CSRF_COOKIE):
        response.delete_cookie(
            name,
            path="/",
            domain=settings.COOKIE_DOMAIN,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )


def _auth_payload(user: User, token: str) -> AuthPayload:
    return AuthPayload(
        user=UserRead.model_validate(user),
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[AuthPayload],
    summary="Create a new account",
    description="Registers a user, then opens a session (HttpOnly JWT cookie + CSRF cookie).",
    responses=_ERRORS,
)
async def register(
    payload: UserCreate, service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    user, token = await service.register(payload)
    response = created(_auth_payload(user, token), "Account created successfully")
    _set_auth_cookies(response, token)
    return response


@router.post(
    "/login",
    response_model=ApiResponse[AuthPayload],
    summary="Log in with email and password",
    responses=_ERRORS,
)
async def login(
    payload: LoginRequest, service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    user, token = await service.login(payload)
    response = ok(_auth_payload(user, token), "Logged in successfully")
    _set_auth_cookies(response, token)
    return response


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="Log out",
    description="Clears the session cookies. Bearer tokens simply expire client-side.",
)
async def logout() -> JSONResponse:
    response = ok(None, "Logged out successfully")
    _clear_auth_cookies(response)
    return response
