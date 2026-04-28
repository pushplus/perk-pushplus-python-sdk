"""开放接口 - 消息接口模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..enums import Channel, SendStatus


@dataclass
class MessageItem:
    """开放接口「消息列表」中的单条消息。"""

    topicName: Optional[str] = None
    messageType: Optional[int] = None
    """消息类型：1-一对一消息，2-一对多消息。"""
    title: Optional[str] = None
    shortCode: Optional[str] = None
    channel: Optional[Channel] = None
    updateTime: Optional[str] = None


@dataclass
class SendMessageResult:
    """查询消息发送结果响应。"""

    status: Optional[int] = None
    """0-未投递，1-发送中，2-已发送，3-发送失败。"""
    errorMessage: Optional[str] = None
    updateTime: Optional[str] = None

    def get_status_enum(self) -> Optional[SendStatus]:
        return SendStatus.of(self.status)


__all__ = ["MessageItem", "SendMessageResult"]
