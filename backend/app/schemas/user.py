import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, model_validator


def _validate_password_strength(value: str) -> str:
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one letter and one digit")
    return value


def _normalize_email(value: str) -> str:
    return value.strip().lower()


Password = Annotated[
    str, Field(min_length=8, max_length=128), AfterValidator(_validate_password_strength)
]
Name = Annotated[str, Field(min_length=2, max_length=100)]
Email = Annotated[EmailStr, AfterValidator(_normalize_email)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserCreate(StrictModel):
    name: Name
    email: Email
    password: Password


class UserUpdate(StrictModel):
    name: Name | None = None
    email: Email | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserUpdate":
        if self.name is None and self.email is None:
            raise ValueError("At least one field (name or email) must be provided")
        return self


class PasswordChange(StrictModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: Password

    @model_validator(mode="after")
    def passwords_differ(self) -> "PasswordChange":
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from the current password")
        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
