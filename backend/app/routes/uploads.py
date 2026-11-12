"""Safe public exposure of uploaded images."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.services.image_service import MIME_BY_EXTENSION, LocalStorage, get_storage
from app.utils.exceptions import NotFoundError

router = APIRouter(tags=["Uploads"])


@router.get("/uploads/{filename}", summary="Serve an uploaded image", include_in_schema=True)
async def serve_upload(filename: str, storage: LocalStorage = Depends(get_storage)) -> FileResponse:
    # Only server-generated names are accepted: no path traversal, no arbitrary files.
    path = storage.path_for(filename)
    if path is None or not path.is_file():
        raise NotFoundError("Image not found")
    return FileResponse(
        path,
        media_type=MIME_BY_EXTENSION[path.suffix.lstrip(".")],
        headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "public, max-age=31536000, immutable",
            "Content-Security-Policy": "default-src 'none'",
        },
    )
