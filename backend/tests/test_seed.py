import asyncio

from fastapi.testclient import TestClient

from app.config.settings import settings
from app.seeds.default_posts import DEFAULT_POSTS
from app.services.image_service import get_storage
from app.services.seed_service import seed_default_posts
from tests.conftest import API, TestSession, csrf_headers, post_form


async def _seed(cfg=settings) -> int:
    async with TestSession() as session:
        return await seed_default_posts(session, get_storage(), cfg)


def test_default_posts_are_seeded_once(client: TestClient, upload_dir) -> None:
    assert asyncio.run(_seed()) == len(DEFAULT_POSTS)
    assert asyncio.run(_seed()) == 0

    data = client.get(f"{API}/posts", params={"size": 50}).json()["data"]
    assert data["total"] == len(DEFAULT_POSTS)
    post = data["items"][0]
    assert post["author"] is None and post["author_id"] is None
    assert post["cover_image_url"]
    assert len(list(upload_dir.iterdir())) == len(DEFAULT_POSTS)
    assert client.get(f"/uploads/{post['cover_image']}").status_code == 200


def test_seeding_can_be_disabled(client: TestClient) -> None:
    disabled = settings.model_copy(update={"SEED_DEFAULT_POSTS": False})
    assert asyncio.run(_seed(disabled)) == 0
    assert client.get(f"{API}/posts").json()["data"]["total"] == 0


def test_editorial_posts_are_read_only(auth_client: TestClient) -> None:
    asyncio.run(_seed())
    post = auth_client.get(f"{API}/posts").json()["data"]["items"][0]
    headers = csrf_headers(auth_client)
    update = auth_client.put(f"{API}/posts/{post['id']}", data=post_form(), headers=headers)
    assert update.status_code == 403
    delete = auth_client.delete(f"{API}/posts/{post['id']}", headers=headers)
    assert delete.status_code == 403
