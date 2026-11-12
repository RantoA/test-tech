"""Endpoints for the authenticated user's profile."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies.auth import get_current_user
from app.handlers.success_handlers import ok
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import PasswordChange, UserRead, UserUpdate
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

_AUTH_ERRORS = {
    401: {"description": "Not authenticated"},
    403: {"description": "Invalid CSRF token"},
    422: {"description": "Validation error"},
}


@router.get(
    "/me", response_model=ApiResponse[UserRead], summary="Get my profile", responses=_AUTH_ERRORS
)
async def get_me(current_user: User = Depends(get_current_user)) -> JSONResponse:
    return ok(UserRead.model_validate(current_user), "Profile retrieved successfully")


@router.put(
    "/me",
    response_model=ApiResponse[UserRead],
    summary="Update my profile (name, email)",
    responses={**_AUTH_ERRORS, 409: {"description": "Email already used"}},
)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user = await service.update_profile(current_user, payload)
    return ok(UserRead.model_validate(user), "Profile updated successfully")


@router.patch(
    "/me/password",
    response_model=ApiResponse[None],
    summary="Change my password",
    responses={**_AUTH_ERRORS, 400: {"description": "Current password is incorrect"}},
)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> JSONResponse:
    await service.change_password(current_user, payload)
    return ok(None, "Password updated successfully")
