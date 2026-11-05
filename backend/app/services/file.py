import uuid
from datetime import timedelta

from fastapi import UploadFile
from minio import Minio, InvalidResponseError
from io import BytesIO

from app.core.config import get_settings_s3

SETTINGS = get_settings_s3()

PRESIGNED_URL_TTL = timedelta(hours=1)


def create_client(url: str) -> Minio:
    return Minio(
        url.replace("http://", "").replace("https://", ""),
        access_key=SETTINGS.s3_root_user,
        secret_key=SETTINGS.s3_root_password,
        secure=url.startswith("https"),
    )


CLIENT = create_client(SETTINGS.s3_url)
PUBLIC_CLIENT = create_client(SETTINGS.s3_public_url or SETTINGS.s3_url)

ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

class UploadError(ValueError):
    pass

class EmptyUploadError(UploadError):
    def __init__(self) -> None:
        super().__init__("Uploaded file is empty")


class UploadTooLargeError(UploadError):
    def __init__(self, size: int, limit: int) -> None:
        self.size = size
        self.limit = limit
        super().__init__(f"File is too large: {size} bytes, limit is {limit} bytes")


class UnsupportedMediaTypeError(UploadError):
    def __init__(self, content_type: str | None) -> None:
        self.content_type = content_type
        allowed = ", ".join(ALLOWED_CONTENT_TYPES)
        message = f"Unsupported media type: {content_type or 'unknown'}. Allowed: {allowed}"
        super().__init__(message)


def init_bucket() -> None:
    try:
        if not CLIENT.bucket_exists(SETTINGS.s3_bucket_name):
            CLIENT.make_bucket(SETTINGS.s3_bucket_name)
    except InvalidResponseError as exc:
        raise RuntimeError(f"Failed to ensure S3 bucket '{SETTINGS.s3_bucket_name}': {exc}") from exc


def size_of(file: UploadFile) -> int:
    if file.size is not None:
        return file.size

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    return size

def validate_image(file: UploadFile, *, max_bytes: int) -> tuple[int, str, str]:
    size = size_of(file)
    if size <= 0:
        raise EmptyUploadError()
    if size > max_bytes:
        raise UploadTooLargeError(size, max_bytes)

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    extension = ALLOWED_CONTENT_TYPES.get(content_type)
    if extension is None:
        raise UnsupportedMediaTypeError(content_type or None)

    return size, extension, content_type


def upload_file(file: UploadFile, *, max_bytes: int) -> str:
    size, ext, content_type = validate_image(file, max_bytes=max_bytes)
    object_name = f"{uuid.uuid4()}{ext}"
    file.file.seek(0)
    content = file.file.read()
    # Blocking, could be run in threadpool
    CLIENT.put_object(
        bucket_name=SETTINGS.s3_bucket_name,
        object_name=object_name,
        data=BytesIO(content),
        length=size,
        content_type=content_type,
    )

    return object_name


def presigned_url(object_name: str) -> str:
    return PUBLIC_CLIENT.presigned_get_object(
        SETTINGS.s3_bucket_name, object_name, expires=PRESIGNED_URL_TTL
    )
