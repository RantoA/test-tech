"""Publishes the default editorial articles (no author account) on first startup."""

import io
import uuid
from datetime import UTC, datetime, timedelta

from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.logging.logger import get_logger
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostFields
from app.seeds.default_posts import DEFAULT_POSTS, SeedPost
from app.services.image_service import StorageBackend

logger = get_logger("seed")

COVER_SIZE = (1600, 900)


def render_cover(background: str, accent: str, seed: int) -> bytes:
    """Draw a sober geometric cover (flat colors, straight lines) as a JPEG."""
    width, height = COVER_SIZE
    image = Image.new("RGB", COVER_SIZE, background)
    draw = ImageDraw.Draw(image)
    step = 100
    for x in range(0, width + 1, step):
        draw.line([(x, 0), (x, height)], fill=accent, width=1)
    for y in range(0, height + 1, step):
        draw.line([(0, y), (width, y)], fill=accent, width=1)
    # A few filled cells, positioned from the seed so every cover differs.
    for i in range(6):
        col = (seed * 3 + i * 5) % (width // step)
        row = (seed + i * 2) % (height // step)
        draw.rectangle([col * step, row * step, (col + 1) * step, (row + 1) * step], fill=accent)
    draw.rectangle([0, height - 24, width, height], fill=accent)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()


async def _create_post(
    posts: PostRepository, storage: StorageBackend, seed: SeedPost, index: int
) -> None:
    fields = PostFields(title=seed["title"], excerpt=seed["excerpt"], content=seed["content"])
    key = f"{uuid.uuid4().hex}.jpg"
    await storage.save(key, render_cover(*seed["palette"], seed=index), "image/jpeg")
    created_at = datetime.now(UTC) - timedelta(days=seed["days_ago"])
    await posts.create(
        title=fields.title,
        slug=seed["slug"],
        excerpt=fields.excerpt,
        content=[block.model_dump(mode="json") for block in fields.content],
        cover_image=key,
        author_id=None,
        created_at=created_at,
        updated_at=created_at,
    )


async def seed_default_posts(
    session: AsyncSession, storage: StorageBackend, settings: Settings
) -> int:
    """Create the default articles that do not exist yet (matched by slug). Returns the count."""
    if not settings.SEED_DEFAULT_POSTS:
        logger.info("Default posts seeding disabled")
        return 0

    posts = PostRepository(session)
    created = 0
    for index, seed in enumerate(DEFAULT_POSTS):
        if await posts.slug_exists(seed["slug"]):
            continue
        await _create_post(posts, storage, seed, index)
        created += 1
    await session.commit()
    logger.info("Default posts seeded", extra={"event": "seed.posts", "posts_created": created})
    return created
