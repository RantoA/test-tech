"""Blog post endpoints (CRUD with cover image upload)."""

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.dependencies.auth import get_current_user
from app.handlers.success_handlers import created, no_content, ok
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.post import PaginatedPosts, PostFields, PostRead, SortOrder
from app.services.post_service import PostService, get_post_service

router = APIRouter(prefix="/posts", tags=["Posts"])

_WRITE_ERRORS = {
    400: {"description": "Invalid image file"},
    401: {"description": "Not authenticated"},
    403: {"description": "Not the author / invalid CSRF token"},
    404: {"description": "Post not found"},
    413: {"description": "Image too large"},
    422: {"description": "Validation error"},
}
CONTENT_DESCRIPTION = (
    'JSON array of blocks, e.g. `[{"type":"heading","text":"Intro"},'
    '{"type":"paragraph","text":"Hello"}]`. Allowed types: heading, subheading, paragraph.'
)


def post_fields_form(
    title: Annotated[str, Form(description="Post title (3-200 chars)")],
    excerpt: Annotated[str, Form(description="Short summary (10-500 chars)")],
    content: Annotated[str, Form(description=CONTENT_DESCRIPTION)],
) -> PostFields:
    """Parse multipart form fields into a validated ``PostFields`` model."""
    try:
        blocks = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RequestValidationError(
            [
                {
                    "type": "json_invalid",
                    "loc": ("body", "content"),
                    "msg": "Content must be valid JSON",
                    "input": content,
                }
            ]
        ) from exc
    try:
        return PostFields(title=title, excerpt=excerpt, content=blocks)
    except ValidationError as exc:
        errors = [{**err, "loc": ("body", *err["loc"])} for err in exc.errors(include_url=False)]
        raise RequestValidationError(errors) from exc


def optional_image(
    image: Annotated[UploadFile | None, File(description="Cover image (JPEG, PNG or WebP)")] = None,
) -> UploadFile | None:
    # Browsers send an empty part when no file is selected.
    if image is None or not image.filename:
        return None
    return image


@router.get(
    "",
    response_model=ApiResponse[PaginatedPosts],
    summary="List posts",
    description="Paginated list with title search, author filter and creation-date sorting.",
)
async def list_posts(
    service: Annotated[PostService, Depends(get_post_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 9,
    search: Annotated[str | None, Query(max_length=100, description="Search in titles")] = None,
    author_id: Annotated[uuid.UUID | None, Query(description="Filter by author")] = None,
    sort: Annotated[SortOrder, Query(description="Sort by creation date")] = "newest",
) -> JSONResponse:
    result = await service.list_posts(
        page=page, size=size, search=search, author_id=author_id, sort=sort
    )
    return ok(result, "Posts retrieved successfully")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[PostRead],
    summary="Create a post",
    responses=_WRITE_ERRORS,
)
async def create_post(
    fields: Annotated[PostFields, Depends(post_fields_form)],
    image: Annotated[UploadFile | None, Depends(optional_image)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[PostService, Depends(get_post_service)],
) -> JSONResponse:
    post = await service.create_post(current_user, fields, image)
    return created(post, "Post created successfully")


@router.get(
    "/{post_id}",
    response_model=ApiResponse[PostRead],
    summary="Get a post",
    responses={404: {"description": "Post not found"}},
)
async def get_post(
    post_id: uuid.UUID, service: Annotated[PostService, Depends(get_post_service)]
) -> JSONResponse:
    return ok(await service.get_post(post_id), "Post retrieved successfully")


@router.put(
    "/{post_id}",
    response_model=ApiResponse[PostRead],
    summary="Update a post",
    description="Replaces title, excerpt and content. Send `image` to replace the cover, "
    "`remove_image=true` to delete it, or neither to keep the current one.",
    responses=_WRITE_ERRORS,
)
async def update_post(
    post_id: uuid.UUID,
    fields: Annotated[PostFields, Depends(post_fields_form)],
    image: Annotated[UploadFile | None, Depends(optional_image)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[PostService, Depends(get_post_service)],
    remove_image: Annotated[bool, Form(description="Remove the current cover image")] = False,
) -> JSONResponse:
    post = await service.update_post(post_id, current_user, fields, image, remove_image)
    return ok(post, "Post updated successfully")


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a post",
    responses={k: v for k, v in _WRITE_ERRORS.items() if k in (401, 403, 404)},
)
async def delete_post(
    post_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[PostService, Depends(get_post_service)],
) -> Response:
    await service.delete_post(post_id, current_user)
    return no_content()
