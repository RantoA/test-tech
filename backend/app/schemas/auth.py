from pydantic import BaseModel, Field

from app.schemas.user import Email, StrictModel, UserRead


class LoginRequest(StrictModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)


class AuthPayload(BaseModel):
    """Returned on login/register. The JWT itself travels in an HttpOnly cookie;
    it is also returned here so the API stays usable from Swagger or other clients."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"
    expires_in: int
