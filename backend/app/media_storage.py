from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from .config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MEDIA_PREFIX = "/media/"


def media_root() -> Path:
    configured = Path(settings.media_root).expanduser()
    return configured if configured.is_absolute() else Path(__file__).resolve().parents[1] / configured


def ensure_media_root() -> Path:
    root = media_root()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        while index < len(data) and data[index] == 0xFF:
            index += 1
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index:index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0)):
            if segment_length < 7:
                return None
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += segment_length
    return None


def _webp_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def inspect_image(data: bytes, declared_type: str | None, filename: str | None) -> tuple[str, int, int]:
    if len(data) > settings.course_image_max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Course cover image must be 5 MB or smaller")
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        detected, dimensions = "image/png", (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))
    elif data.startswith(b"\xff\xd8"):
        detected, dimensions = "image/jpeg", _jpeg_dimensions(data)
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        detected, dimensions = "image/webp", _webp_dimensions(data)
    else:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only valid JPG, PNG, or WebP images are allowed")
    if detected not in ALLOWED_MIME_TYPES or not dimensions or dimensions[0] < 1 or dimensions[1] < 1:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "The uploaded file is not a valid supported image")
    if declared_type and declared_type not in {"application/octet-stream", "application/binary"} and declared_type != detected:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "The file type does not match its image content")
    return detected, dimensions[0], dimensions[1]


async def save_course_image(upload: UploadFile) -> tuple[str, Path, tuple[int, int]]:
    data = await upload.read(settings.course_image_max_bytes + 1)
    detected, width, height = inspect_image(data, upload.content_type, upload.filename)
    extension = ALLOWED_MIME_TYPES[detected]
    key = Path("courses") / f"{uuid4().hex}.{extension}"
    path = ensure_media_root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f"{settings.media_url_prefix.rstrip('/')}/{key.as_posix()}", path, (width, height)


def safe_media_path(url: str | None) -> Path | None:
    if not url or not url.startswith(MEDIA_PREFIX):
        return None
    root = ensure_media_root().resolve()
    candidate = (root / url.removeprefix(MEDIA_PREFIX)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def remove_file_if_safe(url: str | None) -> None:
    path = safe_media_path(url)
    if path and path.is_file():
        path.unlink()
