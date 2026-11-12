#!/bin/sh
set -e

python -m scripts.wait_for_db
# env.py takes a PostgreSQL advisory lock: concurrent containers never migrate at the same time.
alembic upgrade head
# Default editorial articles (created once, skipped afterwards; SEED_DEFAULT_POSTS=false disables).
python -m scripts.seed

exec uvicorn app.main:app --host 0.0.0.0 --port 8005 --proxy-headers --no-access-log "$@"
