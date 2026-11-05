import io

import pytest
from starlette.datastructures import Headers, UploadFile

from app.services.file import (
    EmptyUploadError,
    UnsupportedMediaTypeError,
    UploadTooLargeError,
    validate_image,
)

# https://stackoverflow.com/a/61065546
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"0" * 64
LIMIT = 1024


def make_file(data: bytes, content_type: str | None, name: str = "upload") -> UploadFile:
    headers = Headers({"content-type": content_type}) if content_type else Headers()
    return UploadFile(
        file=io.BytesIO(data),
        size=len(data),
        filename=name,
        headers=headers,
    )


@pytest.mark.parametrize(
    ("data", "content_type", "extension"),
    [
        (PNG, "image/png", ".png"),
        (JPEG, "image/jpeg", ".jpg"),
        (WEBP, "image/webp", ".webp"),
    ],
)
def test_accepts_supported_images(data, content_type, extension):
    size, ext, stored_type = validate_image(make_file(data, content_type), max_bytes=LIMIT)

    assert size == len(data)
    assert ext == extension
    assert stored_type == content_type


def test_strips_content_type_parameters():
    _, ext, stored_type = validate_image(
        make_file(PNG, "image/png; charset=binary"), max_bytes=LIMIT
    )

    assert ext == ".png"
    assert stored_type == "image/png"


def test_rejects_empty_file():
    with pytest.raises(EmptyUploadError):
        validate_image(make_file(b"", "image/png"), max_bytes=LIMIT)


def test_rejects_oversized_file():
    oversized = PNG + b"0" * LIMIT

    with pytest.raises(UploadTooLargeError) as exc_info:
        validate_image(make_file(oversized, "image/png"), max_bytes=LIMIT)

    assert exc_info.value.size == len(oversized)
    assert exc_info.value.limit == LIMIT


def test_rejects_unsupported_content_type():
    with pytest.raises(UnsupportedMediaTypeError):
        validate_image(make_file(b"<html></html>", "text/html"), max_bytes=LIMIT)


def test_rejects_missing_content_type():
    with pytest.raises(UnsupportedMediaTypeError):
        validate_image(make_file(PNG, None), max_bytes=LIMIT)
