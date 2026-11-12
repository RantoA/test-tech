"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "my-blog API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://blog_user:change_me@localhost:5432/blog_manager"
    TEST_DATABASE_URL: str = (
        "postgresql+asyncpg://blog_user:change_me@localhost:5432/blog_manager_test"
    )

    SECRET_KEY: str = Field(default="change_me", min_length=8)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = Field(default=5 * 1024 * 1024, gt=0)
    # Public base URL of the API, used to build absolute image URLs for the browser.
    PUBLIC_API_URL: str = "http://localhost:8005"

    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3005"]

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str | None = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("COOKIE_DOMAIN", mode="before")
    @classmethod
    def empty_domain_is_none(cls, value: object) -> object:
        return value or None

    @model_validator(mode="after")
    def check_production_secrets(self) -> "Settings":
        if self.APP_ENV == "production" and (
            len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("change_me")
        ):
            raise ValueError("SECRET_KEY must be a strong random value (>= 32 chars) in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
