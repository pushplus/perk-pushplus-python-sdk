"""开放接口 - 功能设置模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..enums import Channel


@dataclass
class UserDefaultItem:
    """默认配置列表项。"""

    id: Optional[int] = None
    channel: Optional[Channel] = None
    channelTxt: Optional[str] = None
    updateTime: Optional[str] = None
    name: Optional[str] = None


@dataclass
class UserDefaultDetail:
    """默认配置详情。"""

    id: Optional[int] = None
    channel: Optional[Channel] = None
    option: Optional[str] = None
    pre: Optional[str] = None
    updateTime: Optional[str] = None
    name: Optional[str] = None
    tokenId: Optional[int] = None


@dataclass
class UserDefaultSaveRequest:
    """新增/修改默认配置（修改时需带上 ``id``）。"""

    id: Optional[int] = None
    channel: Optional[Channel] = None
    option: Optional[str] = None
    pre: Optional[str] = None
    tokenId: Optional[int] = None
    """消息令牌 id；用户令牌为 0。"""


__all__ = ["UserDefaultItem", "UserDefaultDetail", "UserDefaultSaveRequest"]
