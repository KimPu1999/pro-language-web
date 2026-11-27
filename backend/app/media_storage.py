from __future__ import annotations

from io import BytesIO
from pathlib import Path
import hashlib
import re
from zipfile import BadZipFile, ZipFile
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from .config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
ALLOWED_DOCUMENT_TYPES = {"application/pdf": "pdf"}
MEDIA_PREFIX = "/media/"


def media_root() -> Path:
    configured = Path(settings.media_root).expanduser()
    return configured if configured.is_absolute() else Path(__file__).resolve().parents[1] / configured

def private_media_root() -> Path:
    configured = Path(settings.media_private_root).expanduser()
    return configured if configured.is_absolute() else Path(__file__).resolve().parents[1] / configured


def ensure_media_root() -> Path:
    root = media_root()
    root.mkdir(parents=True, exist_ok=True)
    return root

def ensure_private_media_root() -> Path:
    root = private_media_root()
    root.mkdir(parents=True, exist_ok=True)
    return root

def storage_status() -> dict[str, object]:
    provider = (settings.media_storage_provider or "").strip().lower()
    if provider in {"s3", "r2", "object_storage"}:
        credentials_ready = bool(settings.media_s3_endpoint and settings.media_s3_bucket and settings.media_s3_region and settings.media_s3_access_key and settings.media_s3_secret_key)
        return {"provider": provider, "configured": credentials_ready, "writable": False, "status": "configured_but_unavailable" if credentials_ready else "not_configured", "detail": "Object storage credentials are present, but this deployment has no object-storage adapter installed." if credentials_ready else "Object storage endpoint, bucket, region, and credentials are incomplete."}
    if provider == "local":
        # Local disk is a development/test provider. Production must use a real
        # object-storage adapter so media is not placed in the web process.
        allowed = settings.app_env.lower() in {"development", "test", "local"}
        try:
            root, private = ensure_media_root(), ensure_private_media_root()
            writable = allowed and root.is_dir() and private.is_dir()
        except OSError:
            writable = False
        return {"provider": "local", "configured": writable, "writable": writable, "status": "ready" if writable else "not_configured", "detail": "Local media storage is available for this deployment." if writable else "Local uploads are disabled or the storage directories are unavailable."}
    return {"provider": provider or "disabled", "configured": False, "writable": False, "status": "not_configured", "detail": "No supported media storage provider is configured."}


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


async def save_project_image(upload: UploadFile) -> tuple[str, Path, tuple[int, int]]:
    """Persist a validated project cover in the shared media store."""
    data = await upload.read(settings.course_image_max_bytes + 1)
    detected, width, height = inspect_image(data, upload.content_type, upload.filename)
    extension = ALLOWED_MIME_TYPES[detected]
    key = Path("projects") / f"{uuid4().hex}.{extension}"
    path = ensure_media_root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f"{settings.media_url_prefix.rstrip('/')}/{key.as_posix()}", path, (width, height)


async def save_roadmap_image(upload: UploadFile) -> tuple[str, Path, tuple[int, int]]:
    """Persist a validated Career Path cover in shared media storage."""
    data = await upload.read(settings.course_image_max_bytes + 1)
    detected, width, height = inspect_image(data, upload.content_type, upload.filename)
    extension = ALLOWED_MIME_TYPES[detected]
    key = Path("roadmaps") / f"{uuid4().hex}.{extension}"
    path = ensure_media_root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f"{settings.media_url_prefix.rstrip('/')}/{key.as_posix()}", path, (width, height)


async def save_media_upload(upload: UploadFile, *, max_bytes: int | None = None, allowed_types: set[str] | None = None) -> tuple[str, Path, str, int, int | None, int | None]:
    """Validate and persist a library asset in the durable shared media root."""
    effective_max_bytes = min(max_bytes or settings.media_max_bytes, settings.media_max_bytes)
    data = await upload.read(effective_max_bytes + 1)
    if len(data) > effective_max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Media file is too large")
    declared = upload.content_type or ""
    if data.startswith(b"%PDF-"):
        detected, extension, dimensions = "application/pdf", "pdf", (None, None)
    else:
        detected, width, height = inspect_image(data, declared, upload.filename)
        extension, dimensions = ALLOWED_MIME_TYPES[detected], (width, height)
    if allowed_types is not None and detected not in allowed_types:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "This file type is disabled by platform media settings")
    if declared and declared not in {"application/octet-stream", "application/binary"} and declared != detected:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "The file type does not match its content")
    key = Path("library") / f"{uuid4().hex}.{extension}"
    path = ensure_media_root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f"{settings.media_url_prefix.rstrip('/')}/{key.as_posix()}", path, detected, len(data), dimensions[0], dimensions[1]


async def save_project_submission_archive(upload: UploadFile) -> tuple[str, Path, str, int]:
    data = await upload.read(settings.project_submission_max_bytes + 1)
    if len(data) > settings.project_submission_max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Project submission archive must be 20 MB or smaller")
    if not (upload.filename or "").lower().endswith(".zip"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only ZIP project submissions are accepted")
    try:
        with ZipFile(BytesIO(data)) as archive:
            total_uncompressed = 0
            for member in archive.infolist():
                name = member.filename.replace("\\", "/")
                if name.startswith("/") or ".." in Path(name).parts:
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Submission archive contains an unsafe path")
                total_uncompressed += member.file_size
            if total_uncompressed > 100 * 1024 * 1024:
                raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Submission archive expands beyond the safe limit")
    except BadZipFile as exc:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "The submission is not a valid ZIP archive") from exc
    key = Path("projects") / "private" / f"{uuid4().hex}.zip"
    path = ensure_media_root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return key.as_posix(), path, upload.filename or "submission.zip", len(data)


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

def safe_private_media_path(key: str | None) -> Path | None:
    if not key or key.startswith("/") or ".." in Path(key).parts:
        return None
    root = ensure_private_media_root().resolve()
    candidate = (root / key).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def normalize_filename(value: str | None) -> str:
    name = Path(value or "upload").name
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip(" .") or "upload"
    return name[:255]


def remove_file_if_safe(url: str | None) -> None:
    path = safe_media_path(url)
    if path and path.is_file():
        path.unlink()
