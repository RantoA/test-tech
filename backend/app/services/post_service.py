"""Post use cases: CRUD, ownership checks, slug generation and cover image lifecycle."""

import math
import secrets
import uuid

from fastapi import Depends, UploadFile
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.logging.logger import get_logger
from app.models.post import Post
from app.models.user import User
from app.repositories.post_repository import PostRepository
from app.schemas.post import PaginatedPosts, PostFields, PostRead, SortOrder
from app.services.image_service import ImageService, get_image_service
from app.utils.exceptions import ForbiddenError, NotFoundError

logger = get_logger("posts")

SLUG_MAX_LENGTH = 200


class PostService:
    def __init__(self, session: AsyncSession, images: ImageService) -> None:
        self.session = session
        self.posts = PostRepository(session)
        self.images = images

    # ---- helpers -------------------------------------------------------------------------

    def to_read(self, post: Post) -> PostRead:
        result = PostRead.model_validate(post)
        result.cover_image_url = self.images.url(post.cover_image)
        return result

    async def _unique_slug(self, title: str, exclude_id: uuid.UUID | None = None) -> str:
        base = slugify(title, max_length=SLUG_MAX_LENGTH, word_boundary=True) or "post"
        slug = base
        while await self.posts.slug_exists(slug, exclude_id):
            slug = f"{base[: SLUG_MAX_LENGTH - 7]}-{secrets.token_hex(3)}"
        return slug

    async def _get_or_404(self, post_id: uuid.UUID) -> Post:
        post = await self.posts.get_by_id(post_id)
        if post is None:
            raise NotFoundError("Post not found")
        return post

    @staticmethod
    def _ensure_owner(post: Post, user: User) -> None:
        if post.author_id != user.id:
            logger.warning(
                "Forbidden post access", extra={"event": "post.forbidden", "post_id": str(post.id)}
            )
            raise ForbiddenError("You can only modify your own posts")

    async def _release_image(self, key: str | None) -> None:
        """Delete an image file once no post references it anymore."""
        if key and await self.posts.count_by_image(key) == 0:
            await self.images.delete(key)

    # ---- queries -------------------------------------------------------------------------

    async def list_posts(
        self,
        *,
        page: int,
        size: int,
        search: str | None,
        author_id: uuid.UUID | None,
        sort: SortOrder,
    ) -> PaginatedPosts:
        items, total = await self.posts.list(
            offset=(page - 1) * size,
            limit=size,
            search=search.strip() if search else None,
            author_id=author_id,
            sort=sort,
        )
        return PaginatedPosts(
            items=[self.to_read(p) for p in items],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total else 0,
        )

    async def get_post(self, post_id: uuid.UUID) -> PostRead:
        return self.to_read(await self._get_or_404(post_id))

    # ---- commands ------------------------------------------------------------------------

    async def create_post(
        self, user: User, fields: PostFields, image: UploadFile | None
    ) -> PostRead:
        image_key = await self.images.save_upload(image) if image else None
        try:
            post = await self.posts.create(
                title=fields.title,
                slug=await self._unique_slug(fields.title),
                excerpt=fields.excerpt,
                content=[block.model_dump(mode="json") for block in fields.content],
                cover_image=image_key,
                author_id=user.id,
            )
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await self.images.delete(image_key)
            raise
        logger.info("Post created", extra={"event": "post.create", "post_id": str(post.id)})
        return self.to_read(post)

    async def update_post(
        self,
        post_id: uuid.UUID,
        user: User,
        fields: PostFields,
        image: UploadFile | None,
        remove_image: bool,
    ) -> PostRead:
        post = await self._get_or_404(post_id)
        self._ensure_owner(post, user)

        old_image = post.cover_image
        new_image = await self.images.save_upload(image) if image else None
        changes: dict[str, object] = {
            "title": fields.title,
            "excerpt": fields.excerpt,
            "content": [block.model_dump(mode="json") for block in fields.content],
        }
        if fields.title != post.title:
            changes["slug"] = await self._unique_slug(fields.title, exclude_id=post.id)
        if new_image:
            changes["cover_image"] = new_image
        elif remove_image:
            changes["cover_image"] = None

        try:
            post = await self.posts.update(post, **changes)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await self.images.delete(new_image)
            raise

        if "cover_image" in changes and old_image and old_image != post.cover_image:
            await self._release_image(old_image)
        logger.info("Post updated", extra={"event": "post.update", "post_id": str(post.id)})
        return self.to_read(post)

    async def delete_post(self, post_id: uuid.UUID, user: User) -> None:
        post = await self._get_or_404(post_id)
        self._ensure_owner(post, user)
        image_key = post.cover_image
        await self.posts.delete(post)
        await self.session.commit()
        await self._release_image(image_key)
        logger.info("Post deleted", extra={"event": "post.delete", "post_id": str(post_id)})


def get_post_service(
    session: AsyncSession = Depends(get_db),
    images: ImageService = Depends(get_image_service),
) -> PostService:
    return PostService(session, images)
