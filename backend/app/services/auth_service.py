"""Registration and authentication use cases."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.security import create_access_token, hash_password, verify_password
from app.logging.logger import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.utils.exceptions import ConflictError, UnauthorizedError

logger = get_logger("auth")

# Used to keep login timing constant when the email is unknown.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, payload: UserCreate) -> tuple[User, str]:
        if await self.users.get_by_email(payload.email):
            logger.warning("Registration rejected: email already used")
            raise ConflictError("An account with this email already exists")
        user = await self.users.create(
            name=payload.name, email=payload.email, hashed_password=hash_password(payload.password)
        )
        await self.session.commit()
        logger.info("User registered", extra={"event": "auth.register", "user_id": str(user.id)})
        return user, create_access_token(user.id)

    async def login(self, payload: LoginRequest) -> tuple[User, str]:
        user = await self.users.get_by_email(payload.email)
        if user is None:
            verify_password(payload.password, _DUMMY_HASH)
            logger.warning("Login failed", extra={"event": "auth.login_failed"})
            raise UnauthorizedError("Invalid email or password")
        if not verify_password(payload.password, user.hashed_password):
            logger.warning(
                "Login failed", extra={"event": "auth.login_failed", "user_id": str(user.id)}
            )
            raise UnauthorizedError("Invalid email or password")
        logger.info("User logged in", extra={"event": "auth.login", "user_id": str(user.id)})
        return user, create_access_token(user.id)


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)
