# my-blog — Blog Post Manager

Full-stack blog post manager built for the **Fintrellis technical assignment**.
Users create an account, then write, edit and delete their own articles, each with
structured content (titles, subtitles, paragraphs) and an optional cover image.

| Layer    | Stack |
|----------|-------|
| Backend  | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, PyJWT, Argon2, Pillow, Pytest, uv |
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, React Hook Form, Zod, Sonner |
| Infra    | PostgreSQL 16, Docker, Docker Compose |

---

## Table of contents

- [my-blog — Blog Post Manager](#my-blog--blog-post-manager)
  - [Table of contents](#table-of-contents)
  - [Quick start](#quick-start)
  - [Features](#features)
  - [Project structure](#project-structure)
  - [Configuration](#configuration)
  - [API reference](#api-reference)
  - [Database \& migrations](#database--migrations)
  - [Tests](#tests)
  - [Local development without Docker](#local-development-without-docker)
  - [Architecture decisions](#architecture-decisions)
  - [Security](#security)

---

## Quick start

**Prerequisites:** Docker 24+ with Docker Compose v2. Nothing else is required.

```bash
git clone <repository-url> my-blog
cd my-blog
docker compose up --build
```

Every variable has a development default, so no `.env` file is needed. To customise the
configuration, run `cp .env.example .env` and edit the values.

| Service      | URL |
|--------------|-----|
| Frontend     | http://localhost:3005 |
| API          | http://localhost:8005/api/v1 |
| Swagger UI   | http://localhost:8005/docs |
| ReDoc        | http://localhost:8005/redoc |
| Health check | http://localhost:8005/health |

Useful commands:

```bash
docker compose up --build -d        # start in the background
docker compose ps                   # service status and health
docker compose logs -f              # follow all logs
docker compose logs -f backend      # follow backend logs (JSON)
docker compose down                 # stop the services (data is kept)
docker compose down -v              # stop and delete volumes (database + uploaded images)
```

> If ports 3005, 8005 or 5452 are already in use, override them in `.env`:
> `FRONTEND_PORT`, `BACKEND_PORT` and `DB_PORT`. When you change the backend port, also update
> `NEXT_PUBLIC_API_URL`, `PUBLIC_API_URL` and `CORS_ORIGINS`.

Startup order is enforced by health checks: `db` (pg_isready) → `backend` (`/health`, which
pings the database) → `frontend`. Before starting Uvicorn, the backend waits for PostgreSQL and
runs `alembic upgrade head`, then publishes the default editorial articles (`scripts/seed.py`, only once).

---

## Features

**Accounts**
- Registration (name, email, password + confirmation), login and logout
- JWT stored in an **HttpOnly cookie**, with CSRF protection by double-submit token
- Profile page: update name and email (uniqueness enforced), change password

**Articles**
- Full CRUD persisted in PostgreSQL. Only the author can edit or delete an article.
- Structured content editor: add, reorder and remove **Title**, **Subtitle** and **Paragraph** blocks
- Summary (excerpt), slug generated automatically and kept unique
- Optional cover image (JPEG, PNG, WebP, 5 MB max) with preview. On edit, the image can be kept, replaced or removed.
- Public listing with pagination, title search, author filter and sorting by creation date
- Dashboard with article count, a table of the user's articles, edit/delete actions with confirmation, and an empty state

**Default content**
- 5 editorial articles about AI are published on first startup, with generated cover images.
  They have no author account (signed "my-blog") and are read-only through the API (403).
  The seed is idempotent (matched by slug); disable it with `SEED_DEFAULT_POSTS=false`.

**Quality**
- Uniform JSON responses `{status, message, data}`, centralized error handlers
- Structured JSON logs with request id, latency and user id
- 49 backend tests (Pytest + TestClient) against an isolated PostgreSQL database
- Responsive UI, with loading, error, empty and success states and toast notifications

---

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # app factory: middleware, handlers, routers, /health
│   │   ├── config/                 # settings (env), async DB engine/session, security helpers
│   │   ├── models/                 # SQLAlchemy models: User, Post
│   │   ├── schemas/                # Pydantic schemas (validation + serialization)
│   │   ├── routes/                 # HTTP layer only: auth, users, posts, uploads
│   │   ├── services/               # business logic: auth, user, post, image (storage abstraction)
│   │   ├── repositories/           # data access (SQLAlchemy queries)
│   │   ├── dependencies/auth.py    # get_current_user (JWT cookie/Bearer + CSRF)
│   │   ├── middleware/             # request logging (request id, latency)
│   │   ├── handlers/               # success helpers, 4xx handlers, 5xx handlers
│   │   ├── logging/                # JSON formatter, logger config, request context
│   │   └── utils/                  # response envelope, domain exceptions
│   ├── migrations/                 # Alembic (async env + versions)
│   ├── scripts/                    # entrypoint.sh, wait_for_db.py
│   ├── tests/                      # conftest, test_auth, test_users, test_posts
│   ├── uploads/                    # local image storage (Docker volume)
│   ├── alembic.ini, pyproject.toml, uv.lock, Dockerfile, .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/login, (auth)/register
│   │   │   ├── (dashboard)/dashboard, posts/new, posts/[id]/edit, profile   # guarded layout
│   │   │   ├── posts/[id]          # public article page
│   │   │   ├── layout.tsx, page.tsx, not-found.tsx
│   │   ├── components/             # ui/, layout/, posts/, auth/, profile/
│   │   ├── services/               # api.ts (fetch wrapper), auth/post/user services
│   │   ├── contexts/AuthContext.tsx
│   │   ├── hooks/                  # useAuth, usePosts, usePost, useDebounce
│   │   ├── schemas/                # Zod schemas (mirror the backend rules)
│   │   ├── types/, utils/
│   │   └── proxy.ts                # optimistic redirects for private/guest-only routes
│   ├── Dockerfile, package.json, .env.example
├── docker/postgres/init-test-db.sh # creates the isolated test database
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Configuration

`.env.example` files document every variable: the root one for Docker Compose, plus
`backend/.env.example` and `frontend/.env.example` for running without Docker.
Never commit a real `.env` file (they are git-ignored).

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development`, `test` or `production`. Debug info in 5xx bodies only in development. Production refuses a weak `SECRET_KEY`. |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `DATABASE_URL` | built by Compose | `postgresql+asyncpg://user:pass@host:5452/db` |
| `TEST_DATABASE_URL` | built by Compose | Isolated database used by the test-suite |
| `SECRET_KEY` | `change_me…` | JWT signing key. Use a random 32+ char value in production (`openssl rand -hex 32`). |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token and cookie lifetime |
| `UPLOAD_DIR` | `uploads` | Image storage directory |
| `MAX_UPLOAD_SIZE` | `5242880` | Max image size in bytes (5 MB) |
| `PUBLIC_API_URL` | `http://localhost:8005` | Base used to build public image URLs |
| `CORS_ORIGINS` | `http://localhost:3005` | Comma-separated allowed origins |
| `COOKIE_SECURE` | `false` | Set `true` behind HTTPS |
| `SEED_DEFAULT_POSTS` | `true` | Publish the default editorial articles on first startup |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8005/api/v1` | API URL used by the browser (build arg) |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `blog_manager` / `blog_user` / `change_me` | Database credentials |

---

## API reference

FastAPI generates two interactive documentations from the OpenAPI schema
(`/openapi.json`). Both always match the code.

### Swagger UI — `/docs`

**http://localhost:8005/docs** lists every endpoint by tag (Authentication, Users, Posts,
Uploads, Health). You can **run requests directly from the browser**. The padlock marks
protected endpoints: call `POST /api/v1/auth/login`, copy `data.access_token`, click
**Authorize** and paste the token (Bearer). Bearer requests do not need a CSRF token.

![Swagger UI: endpoints grouped by tag, with the Authorize button](./images/swagger-ui.png)

### ReDoc — `/redoc`

**http://localhost:8005/redoc** is a read-only reference, convenient for reading each
endpoint in detail:

![ReDoc: detail of PUT /api/v1/users/me](./images/redoc.png)

1. **Navigation**: endpoints grouped by tag, with a search field.
2. **Responses**: every possible status code with its meaning (here 200, 401, 403, 409 and 422).
3. **Endpoint description**: required authorization (`HTTPBearer`) and request body schema
   with the field types.
4. **Samples**: an example request payload and an example response, wrapped in the
   `{status, message, data}` envelope.

All responses use the same envelope:

```json
{ "status": 200, "message": "Post created successfully", "data": { } }
{ "status": 404, "message": "Post not found", "data": null }
{ "status": 422, "message": "Validation error", "data": { "errors": [ { "field": "title", "message": "...", "type": "string_too_short" } ] } }
```

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Create an account (201), opens a session |
| POST | `/api/v1/auth/login` | — | Log in (200) or 401 |
| POST | `/api/v1/auth/logout` | — | Clear session cookies |
| GET | `/api/v1/users/me` | ✔ | Current profile |
| PUT | `/api/v1/users/me` | ✔ | Update name and/or email (409 if email taken) |
| PATCH | `/api/v1/users/me/password` | ✔ | Change password (400 if current password is wrong) |
| GET | `/api/v1/posts` | — | List: `page`, `size` (≤ 50), `search`, `author_id`, `sort=newest\|oldest` |
| POST | `/api/v1/posts` | ✔ | Create (multipart, see below) → 201 |
| GET | `/api/v1/posts/{post_id}` | — | Detail (404 if missing) |
| PUT | `/api/v1/posts/{post_id}` | ✔ author | Update (403 if not the author) |
| DELETE | `/api/v1/posts/{post_id}` | ✔ author | Delete → 204 (also removes the image file) |
| GET | `/uploads/{filename}` | — | Serve an uploaded image |
| GET | `/health` | — | Liveness + database check (503 if DB down) |

**Post payload** (`multipart/form-data`):

| Field | Type | Rules |
|---|---|---|
| `title` | text | 3–200 chars |
| `excerpt` | text | 10–500 chars |
| `content` | JSON string | 1–200 blocks `{"type": "heading"\|"subheading"\|"paragraph", "text": "..."}`, at least one paragraph |
| `image` | file | optional, JPEG/PNG/WebP, ≤ `MAX_UPLOAD_SIZE` |
| `remove_image` | bool | update only: remove the current cover |

Example:

```bash
curl -X POST http://localhost:8005/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F title="Hello world" \
  -F excerpt="My very first article." \
  -F 'content=[{"type":"heading","text":"Intro"},{"type":"paragraph","text":"Hello!"}]' \
  -F image=@cover.jpg
```

Status codes used: `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `413`, `422`, `500`, `503`.

---

## Database & migrations

Migrations live in `backend/migrations/versions` and run automatically when the container
starts. `migrations/env.py` takes a PostgreSQL **advisory lock**, so several backend replicas
starting at the same time never run migrations concurrently.

```bash
docker compose exec backend alembic current                         # current revision
docker compose exec backend alembic upgrade head                    # apply migrations
docker compose exec backend alembic downgrade -1                    # roll back one revision
docker compose exec backend alembic revision --autogenerate -m "msg"  # new migration
```

Schema:
- `users`: id (UUID), name, email (unique), hashed_password, created_at, updated_at
- `posts`: id (UUID), title, slug (unique), content (JSONB blocks), excerpt, cover_image,
  author_id (FK → users, cascade; NULL for editorial posts), created_at, updated_at. Indexes on title, author_id and created_at.

---

## Tests

The tests use Pytest and FastAPI's `TestClient` against a **dedicated PostgreSQL database**
(`blog_manager_test`, created by `docker/postgres/init-test-db.sh`). Tables are recreated at
the start of the session and truncated after each test. Uploads go to a temporary directory.

```bash
# with the stack running
docker compose exec backend pytest

# or locally (needs uv + the db container)
docker compose up -d db
cd backend
TEST_DATABASE_URL=postgresql+asyncpg://blog_user:change_me@localhost:5452/blog_manager_test uv run pytest
```

Coverage: registration (success, duplicate email, validation), login (success, wrong password,
unknown email), invalid/missing token, Bearer auth, CSRF enforcement, logout, profile
update/conflict/validation, password change, post create (with/without image), unique slugs,
listing (pagination, sorting, search, author filter), detail and 404, update, image
keep/replace/remove with file cleanup, delete, **403 on another user's post**, field and
content-block validation, invalid uploads (fake PNG, corrupted file, GIF, file too large → 413),
path traversal on `/uploads`.

Quality checks:

```bash
cd backend && uv run ruff check . && uv run ruff format --check .
cd frontend && npm run lint && npm run build
```

---

## Local development without Docker

```bash
docker compose up -d db                     # PostgreSQL only

cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload        # http://localhost:8005

cd ../frontend
cp .env.example .env.local
npm install
npm run dev                                 # http://localhost:3005
```

---

## Architecture decisions

- **Layered backend.** Routes only handle HTTP (parsing, status codes). Services hold
  business rules (ownership, slugs, image lifecycle, transactions). Repositories hold
  SQLAlchemy queries. Dependencies are injected with `Depends`: session → repository →
  service, so each layer is easy to test or replace.
- **One transaction per use case.** Services commit explicitly. The session dependency rolls
  back on any exception. Old image files are deleted only **after** a successful commit, and a
  newly stored image is removed if the commit fails, so no orphan files and no broken links.
- **Storage abstraction.** `ImageService` depends on a `StorageBackend` interface
  (`save` / `delete` / `url`). `LocalStorage` is the current implementation; an S3-compatible
  backend only needs to implement the same three methods.
- **Structured content.** Articles are stored as typed JSONB blocks
  (heading / subheading / paragraph), validated by Pydantic and rendered as plain React text
  nodes. This gives rich formatting without storing or sanitizing HTML.
- **Exceptions for errors, helpers for success.** Services raise domain exceptions
  (`NotFoundError`, `ForbiddenError`, …), which the `handlers/` package maps to JSON responses.
  2xx responses are built by `handlers/success_handlers.py`.
- **Frontend state.** React Context for the session, small custom hooks for data fetching,
  React Hook Form + Zod for forms. No extra state library.
- **Design.** Sober SaaS look: one accent color, square corners (images included), thin
  borders instead of shadows, no gradients or decorative animations.

---

## Security

- Passwords hashed with **Argon2** (`argon2-cffi`). Constant-time login for unknown emails.
- **JWT in an HttpOnly cookie** (`SameSite=Lax`, `Secure` configurable), so it is not readable
  by JavaScript. Bearer tokens are also accepted for API clients and Swagger.
- **CSRF protection**: for cookie-authenticated mutations, the `X-CSRF-Token` header must
  match the `csrf_token` cookie (double submit, constant-time comparison).
- **Authorization** is enforced server-side: only the author can update or delete a post (403).
  The Next.js proxy and the guarded layout are UX-only redirects.
- **Upload hardening**: the client filename and Content-Type are ignored. The real format is
  checked with magic bytes and Pillow `verify()` (JPEG/PNG/WebP only). Size is limited while
  streaming (413). Pillow's decompression-bomb guard is on. File names are random UUIDs.
  Images are served by a dedicated route that only accepts generated names (no path
  traversal), with `nosniff` and a restrictive CSP.
- **Strict validation** on both sides (Pydantic with `extra="forbid"`, Zod). SQL is built with
  SQLAlchemy parameters, and `LIKE` wildcards are escaped in search.
- **No sensitive data leaks**: generic 500/503 messages (debug details only in development),
  password hashes never serialized, and passwords/tokens never logged (sensitive keys masked).
- CORS restricted to the configured origins. Security headers on the frontend. Containers
  run as non-root users. Production startup fails if `SECRET_KEY` is weak.
