"""Block until PostgreSQL accepts connections (bounded retries)."""

import asyncio
import sys

import asyncpg

from app.config.settings import settings

MAX_ATTEMPTS = 30
DELAY_SECONDS = 2


async def main() -> int:
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            connection = await asyncpg.connect(dsn, timeout=5)
            await connection.close()
            print("Database is ready", flush=True)
            return 0
        except (OSError, asyncpg.PostgresError) as exc:
            print(f"Waiting for database ({attempt}/{MAX_ATTEMPTS}): {exc}", flush=True)
            await asyncio.sleep(DELAY_SECONDS)
    print("Database not reachable, giving up", file=sys.stderr, flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
