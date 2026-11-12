"""Profile management use cases for the authenticated user."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.security import hash_password, verify_password
from app.logging.logger import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordChange, UserUpdate
from app.utils.exceptions import BadRequestError, ConflictError

logger = get_logger("users")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def update_profile(self, user: User, payload: UserUpdate) -> User:
        changes = payload.model_dump(exclude_none=True)
        new_email = changes.get("email")
        if new_email and new_email != user.email:
            existing = await self.users.get_by_email(new_email)
            if existing and existing.id != user.id:
                raise ConflictError("An account with this email already exists")
        user = await self.users.update(user, **changes)
        await self.session.commit()
        logger.info("Profile updated", extra={"event": "user.update", "fields": sorted(changes)})
        return user

    async def change_password(self, user: User, payload: PasswordChange) -> None:
        if not verify_password(payload.current_password, user.hashed_password):
            logger.warning("Password change rejected", extra={"event": "user.password_failed"})
            raise BadRequestError("Current password is incorrect")
        await self.users.update(user, hashed_password=hash_password(payload.new_password))
        await self.session.commit()
        logger.info("Password changed", extra={"event": "user.password_changed"})


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)
