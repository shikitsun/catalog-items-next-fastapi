import io
import os
import uuid
from fastapi import UploadFile
from minio import Minio, InvalidResponseError

from app.core.config import get_settings_s3

SETTINGS = get_settings_s3()

# Retrieve only host and port
HOST = SETTINGS.s3_url.replace("http://", "").replace("https://", "")
PROTOCOL = "https" if SETTINGS.s3_url.find("https") == -1  else "http"

CLIENT = Minio(
    HOST,
    access_key=SETTINGS.s3_root_user,
    secret_key=SETTINGS.s3_root_password,
    # If protocol are https - it is secure, otherwise likely it was running inside
    secure=PROTOCOL == "https",
)


def init_bucket() -> None:
    try:
        if not CLIENT.bucket_exists(SETTINGS.s3_bucket_name):
            CLIENT.make_bucket(SETTINGS.s3_bucket_name)
    except InvalidResponseError as exc:
        raise RuntimeError(f"Failed to ensure S3 bucket '{SETTINGS.s3_bucket_name}': {exc}") from exc


def upload_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1]
    object_name = f"{uuid.uuid4()}{ext}"

    file.file.seek(0)
    content = file.file.read()

    CLIENT.put_object(
        bucket_name=SETTINGS.s3_bucket_name,
        object_name=object_name,
        data=io.BytesIO(content),
        length=len(content),
        content_type=file.content_type or "application/octet-stream",
    )

    return f"{PROTOCOL}://{HOST}/{SETTINGS.s3_bucket_name}/{object_name}"
