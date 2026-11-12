"""Seed the default editorial articles. Safe to run on every startup."""

import asyncio

from app.config.database import SessionLocal, engine
from app.config.settings import settings
from app.logging.logger import configure_logging
from app.services.image_service import get_storage
from app.services.seed_service import seed_default_posts


async def main() -> None:
    configure_logging()
    try:
        async with SessionLocal() as session:
            await seed_default_posts(session, get_storage(), settings)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
