"""开放接口 - 图片服务（文档「十二. 图片服务接口」）。

包含 4 个接口：

1. :meth:`ImageApi.get_upload_token` 获取上传凭证
2. :meth:`ImageApi.upload` 上传图片到七牛云（multipart/form-data，不带 ``access-key``）
3. :meth:`ImageApi.list` 已上传图片列表
4. :meth:`ImageApi.delete` 主动删除图片

另外提供 :meth:`upload_file` / :meth:`upload_bytes` / :meth:`upload_stream` 等
便捷方法，内部自动「先取凭证 → 再上传」。仅支持图片类型，30 天有效期。
"""
from __future__ import annotations

import json
import mimetypes
import os
import uuid
from pathlib import Path
from typing import IO, Optional, Union

from ..exceptions import PushPlusError
from ..http import call_execute_raw
from ..models import ImageItem, ImageUploadResult, ImageUploadToken, PageQuery, PageResult
from ..models.base import model_from_dict
from .base import OpenAbstractApi


PathLike = Union[str, "os.PathLike[str]", Path]


class ImageApi(OpenAbstractApi):
    """图片服务相关接口。"""

    # ------------------------ 1. 获取上传凭证 ------------------------

    def get_upload_token(self) -> ImageUploadToken:
        """1. 获取上传凭证。"""

        return self.execute_open(
            "GET", "/api/open/userImage/uploadToken", None, ImageUploadToken
        )

    # ------------------------ 2. 上传图片 ------------------------

    def upload(
        self,
        token: ImageUploadToken,
        file_bytes: bytes,
        file_name: str,
        content_type: Optional[str] = None,
    ) -> ImageUploadResult:
        """2. 上传图片到七牛云。

        使用「获取上传凭证」返回的 ``uploadUrl`` 与 ``uploadToken``，
        按七牛云表单上传规范以 ``multipart/form-data`` 提交。该请求
        **不会** 携带 PushPlus 的 ``access-key`` 头。
        """

        if token is None:
            raise PushPlusError("上传凭证 token 不能为 None")
        if not token.uploadToken:
            raise PushPlusError("上传凭证 uploadToken 不能为空")
        upload_url = token.uploadUrl or token.uploadHost
        if not upload_url:
            raise PushPlusError("上传凭证未返回 uploadUrl/uploadHost")
        return self.upload_to_qiniu(
            upload_url, token.uploadToken, file_bytes, file_name, content_type
        )

    def upload_to_qiniu(
        self,
        upload_url: str,
        upload_token: str,
        file_bytes: bytes,
        file_name: str,
        content_type: Optional[str] = None,
    ) -> ImageUploadResult:
        """2. 上传图片到七牛云（低层方法）。直接指定上传地址与 token。"""

        if not upload_url:
            raise PushPlusError("upload_url 不能为空")
        if not upload_token:
            raise PushPlusError("upload_token 不能为空")
        if file_bytes is None or len(file_bytes) == 0:
            raise PushPlusError("上传文件内容不能为空")

        safe_name = file_name if file_name else "file"
        mime = content_type or "application/octet-stream"

        boundary = "----PushPlusBoundary" + uuid.uuid4().hex
        body = _build_multipart_body(boundary, upload_token, safe_name, mime, file_bytes)

        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        resp = call_execute_raw(self.http, "POST", upload_url, headers, body)
        if not resp.is_successful:
            raise PushPlusError(
                f"上传图片到七牛云失败: status={resp.status_code}, body={resp.body}",
                code=resp.status_code,
            )
        try:
            payload = json.loads(resp.body) if resp.body else {}
        except (TypeError, ValueError) as exc:
            raise PushPlusError(
                f"解析七牛云响应失败: {exc}, payload={resp.body}", cause=exc
            ) from exc
        if not isinstance(payload, dict):
            raise PushPlusError(f"七牛云返回非 JSON 对象: {resp.body}")
        result = model_from_dict(ImageUploadResult, payload)
        if result is None:
            raise PushPlusError("七牛云上传响应为空")
        if not result.is_success():
            raise PushPlusError(
                f"七牛云上传失败: errno={result.errno}, msg={result.msg}",
                code=result.errno if result.errno is not None else -1,
            )
        return result

    # ------------------------ 便捷上传方法 ------------------------

    def upload_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
        content_type: Optional[str] = None,
    ) -> ImageUploadResult:
        """便捷方法：自动获取上传凭证后上传字节数组。"""

        mime = content_type or _guess_content_type_by_name(file_name)
        token = self.get_upload_token()
        return self.upload(token, file_bytes, file_name, mime)

    def upload_file(
        self,
        file_path: PathLike,
        content_type: Optional[str] = None,
    ) -> ImageUploadResult:
        """便捷方法：自动获取上传凭证后上传指定路径的文件。"""

        if file_path is None:
            raise PushPlusError("上传文件路径不能为 None")
        path = Path(file_path)
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise PushPlusError(f"读取上传文件失败: {exc}", cause=exc) from exc
        file_name = path.name or "file"
        mime = content_type
        if mime is None:
            guess, _ = mimetypes.guess_type(file_name)
            mime = guess or _guess_content_type_by_name(file_name)
        return self.upload_bytes(data, file_name, mime)

    def upload_stream(
        self,
        stream: IO[bytes],
        file_name: str,
        content_type: Optional[str] = None,
    ) -> ImageUploadResult:
        """便捷方法：自动获取上传凭证后上传输入流（不关闭传入的流）。"""

        if stream is None:
            raise PushPlusError("输入流不能为 None")
        data = stream.read()
        if not isinstance(data, (bytes, bytearray)):
            raise PushPlusError("输入流应返回 bytes 数据")
        return self.upload_bytes(bytes(data), file_name, content_type)

    # ------------------------ 3. 图片列表 ------------------------

    def list(self, query: Optional[PageQuery] = None) -> PageResult[ImageItem]:
        """3. 图片列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/userImage/list", body, PageResult[ImageItem]
        )
        return result or PageResult(list=[])

    # ------------------------ 4. 删除图片 ------------------------

    def delete(self, id_: int) -> None:
        """4. 主动删除图片；未删除的图片默认 30 天后由系统自动清理。"""

        path = self.append_query("/api/open/userImage/delete", {"id": int(id_)})
        self.execute_open("DELETE", path, None, None)


def _build_multipart_body(
    boundary: str,
    upload_token: str,
    file_name: str,
    content_type: str,
    file_bytes: bytes,
) -> bytes:
    crlf = b"\r\n"
    parts = []
    parts.append(f"--{boundary}".encode("utf-8"))
    parts.append(b'Content-Disposition: form-data; name="token"')
    parts.append(b"")
    parts.append(upload_token.encode("utf-8"))

    parts.append(f"--{boundary}".encode("utf-8"))
    disp = 'Content-Disposition: form-data; name="file"; filename="{}"'.format(
        _escape_file_name(file_name)
    )
    parts.append(disp.encode("utf-8"))
    parts.append(f"Content-Type: {content_type}".encode("utf-8"))
    parts.append(b"")
    parts.append(file_bytes)

    parts.append(f"--{boundary}--".encode("utf-8"))
    parts.append(b"")
    return crlf.join(parts)


def _escape_file_name(name: str) -> str:
    return name.replace('"', "_").replace("\r", " ").replace("\n", " ")


def _guess_content_type_by_name(name: Optional[str]) -> str:
    if not name:
        return "application/octet-stream"
    lower = name.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        return "image/jpeg"
    if lower.endswith(".gif"):
        return "image/gif"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".bmp"):
        return "image/bmp"
    if lower.endswith(".svg"):
        return "image/svg+xml"
    return "application/octet-stream"


__all__ = ["ImageApi"]
