"""开放接口 - 微信 ClawBot 模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClawBotQrCode:
    """ClawBot 二维码。"""

    url: Optional[str] = None
    qrcode: Optional[str] = None


@dataclass
class ClawBotInfo:
    """ClawBot 绑定详情。"""

    createTime: Optional[str] = None
    haveContextToken: Optional[int] = None
    """是否有对话令牌（文档为字符串/数字混用，统一用 int 兼容）。"""


@dataclass
class ClawBotMessage:
    """ClawBot 发送消息。"""

    type: Optional[int] = None
    """1-文字，3-语音。"""
    text: Optional[str] = None


__all__ = ["ClawBotQrCode", "ClawBotInfo", "ClawBotMessage"]
