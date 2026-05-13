"""开放接口 - 图片服务模型（文档「十二. 图片服务接口」）。

图片服务底层使用七牛云存储：

- :class:`ImageUploadToken` 是 PushPlus 颁发的七牛云上传凭证及上传域名等元数据。
- :class:`ImageUploadResult` 是七牛云 multipart 上传后的响应（非 PushPlus 统一结构）。
- :class:`ImageItem` 是 PushPlus 「图片列表」接口返回的单项数据。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageUploadToken:
    """图片服务 - 获取上传凭证响应。"""

    uploadToken: Optional[str] = None
    """七牛云上传凭证。"""
    uploadHost: Optional[str] = None
    """七牛云上传域名，例如 ``https://upload.qiniup.com``。"""
    uploadUrl: Optional[str] = None
    """七牛云上传地址，一般等同于 ``uploadHost + "/"``。"""
    bucket: Optional[str] = None
    """七牛云存储桶名称。"""
    expiresIn: Optional[int] = None
    """凭证有效时间（秒）。"""


@dataclass
class ImageUploadResult:
    """图片服务 - 上传图片响应（由七牛云直接返回）。

    注意：该响应不是 PushPlus 统一的 ``{code, msg, data}`` 结构，
    判断成功使用 :meth:`is_success`（``errno`` 为 0）。
    """

    errno: Optional[int] = None
    """错误码；0 表示成功。"""
    ext: Optional[str] = None
    """文件扩展名，例如 ``.png``。"""
    fname: Optional[str] = None
    """文件名。"""
    fsize: Optional[int] = None
    """文件大小（字节）。"""
    hash: Optional[str] = None
    """七牛云文件 hash。"""
    key: Optional[str] = None
    """对象存储中的路径 key。"""
    mimeType: Optional[str] = None
    """MIME 类型。"""
    msg: Optional[str] = None
    """响应说明。"""
    thumbnail: Optional[str] = None
    """缩略图地址。"""
    url: Optional[str] = None
    """图片访问地址。"""

    def is_success(self) -> bool:
        """是否上传成功（``errno`` 为 0）。"""

        return self.errno is not None and int(self.errno) == 0


@dataclass
class ImageItem:
    """图片服务 - 图片列表项。"""

    id: Optional[int] = None
    """图片 id。"""
    imgUrl: Optional[str] = None
    """图片地址。"""
    thumbnail: Optional[str] = None
    """缩略图地址。"""
    createTime: Optional[str] = None
    """创建时间。"""


__all__ = ["ImageUploadToken", "ImageUploadResult", "ImageItem"]
