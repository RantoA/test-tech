"""Test fixtures: an isolated PostgreSQL test database, a TestClient and authenticated users."""

import asyncio
import io
import os
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

import pytest

os.environ["APP_ENV"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://blog_user:change_me@localhost:5452/blog_manager_test",
)

from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402
from sqlalchemy import NullPool, text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.config.database import Base, get_db  # noqa: E402
from app.config.security import CSRF_COOKIE, CSRF_HEADER  # noqa: E402
from app.config.settings import settings  # noqa: E402
from app.main import app  # noqa: E402

API = "/api/v1"
DEFAULT_PASSWORD = "Password123"

# NullPool: each TestClient runs its own event loop, so connections must not be reused.
test_engine = create_async_engine(os.environ["DATABASE_URL"], poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False, autoflush=False)


async def override_get_db() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def _reset_schema() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def _truncate() -> None:
    async with test_engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session", autouse=True)
def database() -> Iterator[None]:
    asyncio.run(_reset_schema())
    yield
    asyncio.run(test_engine.dispose())


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path / "uploads")
    yield
    asyncio.run(_truncate())


@pytest.fixture
def upload_dir():
    return settings.UPLOAD_DIR


def _make_client() -> TestClient:
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with _make_client() as test_client:
        yield test_client


def csrf_headers(test_client: TestClient) -> dict[str, str]:
    return {CSRF_HEADER: test_client.cookies.get(CSRF_COOKIE) or ""}


def register_user(
    test_client: TestClient,
    name: str = "Alice Martin",
    email: str = "alice@example.com",
    password: str = DEFAULT_PASSWORD,
) -> dict[str, Any]:
    response = test_client.post(
        f"{API}/auth/register", json={"name": name, "email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """A client logged in through cookies (the browser flow)."""
    register_user(client)
    return client


@pytest.fixture
def other_client() -> Iterator[TestClient]:
    """A second, independent user session."""
    with _make_client() as test_client:
        register_user(test_client, name="Bob Durand", email="bob@example.com")
        yield test_client


def make_image(fmt: str = "PNG", size: tuple[int, int] = (32, 24)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color=(40, 90, 160)).save(buffer, format=fmt)
    return buffer.getvalue()


SAMPLE_CONTENT = (
    '[{"type":"heading","text":"Introduction"},'
    '{"type":"subheading","text":"Context"},'
    '{"type":"paragraph","text":"This is the first paragraph of the post."}]'
)


def post_form(**overrides: str) -> dict[str, str]:
    data = {
        "title": "My first post",
        "excerpt": "A short summary of the post.",
        "content": SAMPLE_CONTENT,
    }
    data.update(overrides)
    return data


@pytest.fixture
def create_post(auth_client: TestClient) -> Callable[..., dict[str, Any]]:
    def _create(image: bytes | None = None, **overrides: str) -> dict[str, Any]:
        files = {"image": ("cover.png", image, "image/png")} if image else None
        response = auth_client.post(
            f"{API}/posts",
            data=post_form(**overrides),
            files=files,
            headers=csrf_headers(auth_client),
        )
        assert response.status_code == 201, response.text
        return response.json()["data"]

    return _create
