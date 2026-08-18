"""构造仅含一个 file 字段的 multipart/form-data 请求体。"""
from __future__ import annotations

import uuid
from typing import Optional, Tuple

from .exceptions import PushPlusError


def build_file_multipart(
    file_name: str,
    content_type: Optional[str],
    file_bytes: bytes,
) -> Tuple[str, bytes]:
    """返回 ``(Content-Type, body)``。"""

    if not file_bytes:
        raise PushPlusError("上传文件内容不能为空")
    safe_name = file_name.strip() if file_name and file_name.strip() else "file"
    mime = content_type.strip() if content_type and content_type.strip() else "application/octet-stream"
    boundary = "----PushPlusBoundary" + uuid.uuid4().hex
    crlf = b"\r\n"
    parts = [
        f"--{boundary}".encode("utf-8"),
        (
            'Content-Disposition: form-data; name="file"; filename="{}"'.format(
                _escape_file_name(safe_name)
            )
        ).encode("utf-8"),
        f"Content-Type: {mime}".encode("utf-8"),
        b"",
        file_bytes,
        f"--{boundary}--".encode("utf-8"),
        b"",
    ]
    return f"multipart/form-data; boundary={boundary}", crlf.join(parts)


def _escape_file_name(name: str) -> str:
    return name.replace('"', "_").replace("\r", " ").replace("\n", " ")


__all__ = ["build_file_multipart"]
