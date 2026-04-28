"""开放接口 - 消息 token 模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MessageTokenItem:
    """消息 token 列表项。"""

    id: Optional[int] = None
    name: Optional[str] = None
    expireTime: Optional[str] = None
    token: Optional[str] = None


@dataclass
class MessageTokenOption:
    """消息 token 下拉选项（仅 id + name）。"""

    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class MessageTokenAddRequest:
    """新增消息 token 请求。"""

    name: Optional[str] = None
    expireTime: Optional[str] = None
    """过期时间，格式 ``yyyy-MM-dd`` 或 ``yyyy-MM-dd HH:mm:ss``；不填默认 ``2999-12-31``。"""


@dataclass
class MessageTokenEditRequest:
    """修改消息 token 请求。"""

    id: Optional[int] = None
    name: Optional[str] = None
    expireTime: Optional[str] = None


__all__ = [
    "MessageTokenItem",
    "MessageTokenOption",
    "MessageTokenAddRequest",
    "MessageTokenEditRequest",
]
