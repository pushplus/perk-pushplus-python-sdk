"""开放接口 - 新消息 ClawBot 模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CmccBindRequest:
    """新消息 ClawBot 绑定请求。"""

    apiKey: str
    """中国移动新消息 Channel API Key，必须以 ak_ 或 app_ 开头。"""


@dataclass
class CmccInfo:
    """新消息 ClawBot 绑定状态。"""

    bound: Optional[int] = None
    """是否已绑定；0-未绑定，1-已绑定。"""
    apiKeyMasked: Optional[str] = None
    """脱敏后的 API Key。"""
    createTime: Optional[str] = None
    """绑定时间。"""


__all__ = ["CmccBindRequest", "CmccInfo"]
