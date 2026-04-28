"""开放接口 - 好友功能模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class FriendItem:
    """好友列表项。"""

    id: Optional[int] = None
    friendId: Optional[int] = None
    token: Optional[str] = None
    headImgUrl: Optional[str] = None
    nickName: Optional[str] = None
    emailStatus: Optional[int] = None
    havePhone: Optional[int] = None
    isFollow: Optional[int] = None
    remark: Optional[str] = None
    createTime: Optional[str] = None


@dataclass
class FriendQrCode:
    """好友二维码（个人二维码）。"""

    qrCodeImgUrl: Optional[str] = None


__all__ = ["FriendItem", "FriendQrCode"]
