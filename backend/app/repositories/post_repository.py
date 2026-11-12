"""Data access for posts: CRUD plus filtered, sorted and paginated listing."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import SortOrder


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, post_id: uuid.UUID) -> Post | None:
        return await self.session.get(Post, post_id)

    async def slug_exists(self, slug: str, exclude_id: uuid.UUID | None = None) -> bool:
        stmt = select(Post.id).where(Post.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Post.id != exclude_id)
        result = await self.session.execute(stmt.limit(1))
        return result.first() is not None

    async def count_by_image(self, image_key: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(Post.cover_image == image_key)
        )
        return int(result.scalar_one())

    async def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        author_id: uuid.UUID | None = None,
        sort: SortOrder = "newest",
    ) -> tuple[list[Post], int]:
        filters = []
        if search:
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            filters.append(Post.title.ilike(f"%{escaped}%", escape="\\"))
        if author_id is not None:
            filters.append(Post.author_id == author_id)

        total_result = await self.session.execute(
            select(func.count()).select_from(Post).where(*filters)
        )
        total = int(total_result.scalar_one())

        order = Post.created_at.desc() if sort == "newest" else Post.created_at.asc()
        result = await self.session.execute(
            select(Post).where(*filters).order_by(order, Post.id).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, **fields: Any) -> Post:
        post = Post(**fields)
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def update(self, post: Post, **fields: Any) -> Post:
        for key, value in fields.items():
            setattr(post, key, value)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.flush()
