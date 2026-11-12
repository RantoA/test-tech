import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Post(TimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (Index("ix_posts_created_at", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    # Structured content: [{"type": "heading" | "subheading" | "paragraph", "text": "..."}]
    content: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    # Storage key of the cover image (file name for local storage), or None.
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    author: Mapped["User"] = relationship(back_populates="posts", lazy="joined")
