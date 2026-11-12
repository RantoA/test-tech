"""Image validation and storage.

Storage is abstracted behind ``StorageBackend`` so the local filesystem implementation can later
be swapped for an S3-compatible backend without touching the post service.
"""

import io
import re
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.config.settings import settings
from app.logging.logger import get_logger
from app.utils.exceptions import BadRequestError, PayloadTooLargeError

logger = get_logger("images")

CHUNK_SIZE = 64 * 1024
# Pillow format name -> (file extension, MIME type)
ALLOWED_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}
IMAGE_KEY_PATTERN = re.compile(r"^[0-9a-f]{32}\.(jpg|png|webp)$")
MIME_BY_EXTENSION = {ext: mime for ext, mime in ALLOWED_FORMATS.values()}
# Guard against decompression bombs.
Image.MAX_IMAGE_PIXELS = 40_000_000


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    def url(self, key: str) -> str: ...


class LocalStorage(StorageBackend):
    def __init__(self, base_dir: Path, public_base_url: str) -> None:
        self.base_dir = base_dir
        self.public_base_url = public_base_url.rstrip("/")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path | None:
        if not IMAGE_KEY_PATTERN.fullmatch(key):
            return None
        return self.base_dir / key

    async def save(self, key: str, data: bytes, content_type: str) -> None:
        path = self.path_for(key)
        if path is None:
            raise ValueError("Invalid storage key")
        path.write_bytes(data)

    async def delete(self, key: str) -> None:
        path = self.path_for(key)
        if path is not None:
            path.unlink(missing_ok=True)

    def url(self, key: str) -> str:
        return f"{self.public_base_url}/uploads/{key}"


def _detect_format_from_magic(header: bytes) -> str | None:
    if header.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "WEBP"
    return None


class ImageService:
    def __init__(self, storage: StorageBackend, max_size: int) -> None:
        self.storage = storage
        self.max_size = max_size

    async def _read_limited(self, upload: UploadFile) -> bytes:
        buffer = bytearray()
        while chunk := await upload.read(CHUNK_SIZE):
            buffer.extend(chunk)
            if len(buffer) > self.max_size:
                raise PayloadTooLargeError(
                    f"Image exceeds the maximum size of {self.max_size // (1024 * 1024)} MB"
                )
        return bytes(buffer)

    def _validate(self, data: bytes) -> str:
        """Return the real image format, never trusting the client filename or Content-Type."""
        if not data:
            raise BadRequestError("Uploaded image is empty")
        magic_format = _detect_format_from_magic(data[:16])
        if magic_format is None:
            raise BadRequestError("Unsupported image format. Allowed formats: JPEG, PNG, WebP")
        try:
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
                real_format = image.format
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
            raise BadRequestError("Uploaded file is not a valid image") from exc
        if real_format != magic_format or real_format not in ALLOWED_FORMATS:
            raise BadRequestError("Unsupported image format. Allowed formats: JPEG, PNG, WebP")
        return real_format

    async def save_upload(self, upload: UploadFile) -> str:
        """Validate and store an uploaded image, returning its storage key."""
        data = await self._read_limited(upload)
        image_format = self._validate(data)
        extension, mime = ALLOWED_FORMATS[image_format]
        key = f"{uuid.uuid4().hex}.{extension}"
        await self.storage.save(key, data, mime)
        logger.info("Image stored", extra={"image_key": key, "size": len(data), "format": mime})
        return key

    async def delete(self, key: str | None) -> None:
        if key:
            await self.storage.delete(key)
            logger.info("Image deleted", extra={"image_key": key})

    def url(self, key: str | None) -> str | None:
        return self.storage.url(key) if key else None


def get_storage() -> LocalStorage:
    return LocalStorage(settings.UPLOAD_DIR, settings.PUBLIC_API_URL)


def get_image_service() -> ImageService:
    return ImageService(get_storage(), settings.MAX_UPLOAD_SIZE)
