FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Dependencies first for better layer caching (dev group kept so tests run in the container).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

RUN groupadd --system app && useradd --system --gid app --home /app app \
    && mkdir -p /app/uploads && chown -R app:app /app /opt/venv

USER app
EXPOSE 8005

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
