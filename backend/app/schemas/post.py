import uuid
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.schemas.user import AuthorRead

MAX_BLOCKS = 200


class BlockType(StrEnum):
    HEADING = "heading"
    SUBHEADING = "subheading"
    PARAGRAPH = "paragraph"


BLOCK_MAX_LENGTH = {BlockType.HEADING: 200, BlockType.SUBHEADING: 200, BlockType.PARAGRAPH: 10_000}


class ContentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    type: BlockType
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def check_length(cls, value: str, info: ValidationInfo) -> str:
        block_type = info.data.get("type")
        limit = BLOCK_MAX_LENGTH.get(block_type, 10_000)
        if len(value) > limit:
            raise ValueError(f"Block text must be at most {limit} characters")
        return value


def _validate_blocks(blocks: list[ContentBlock]) -> list[ContentBlock]:
    if not any(block.type == BlockType.PARAGRAPH for block in blocks):
        raise ValueError("Content must contain at least one paragraph")
    return blocks


class PostFields(BaseModel):
    """Validated textual fields of a post (shared by create and update)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=200)
    excerpt: str = Field(min_length=10, max_length=500)
    content: list[ContentBlock] = Field(min_length=1, max_length=MAX_BLOCKS)

    @field_validator("content")
    @classmethod
    def content_has_paragraph(cls, value: list[ContentBlock]) -> list[ContentBlock]:
        return _validate_blocks(value)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    excerpt: str
    content: list[ContentBlock]
    cover_image: str | None
    cover_image_url: str | None = None
    author_id: uuid.UUID
    author: AuthorRead
    created_at: datetime
    updated_at: datetime


class PaginatedPosts(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    size: int
    pages: int


SortOrder = Literal["newest", "oldest"]
