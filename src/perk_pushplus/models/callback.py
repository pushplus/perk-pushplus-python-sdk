"""消息回调相关数据模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..enums import CallbackEvent, SendStatus


@dataclass
class MessageCompleteInfo:
    """消息完成回调中的 ``messageInfo`` 字段。"""

    message: Optional[str] = None
    """推送错误内容（如有）。"""
    shortCode: Optional[str] = None
    """消息流水号。"""
    sendStatus: Optional[int] = None
    """发送状态：0-未发送，1-发送中，2-发送成功，3-发送失败。"""

    def get_send_status_enum(self) -> Optional[SendStatus]:
        return SendStatus.of(self.sendStatus)


@dataclass
class TopicUserInfo:
    """群组新增用户回调中的 ``topicUserInfo`` 字段。"""

    id: Optional[int] = None
    openId: Optional[str] = None
    topicId: Optional[int] = None
    userSex: Optional[int] = None
    isFollow: Optional[int] = None
    nickName: Optional[str] = None
    havePhone: Optional[int] = None
    topicCode: Optional[str] = None
    topicName: Optional[str] = None
    headImgUrl: Optional[str] = None
    emailStatus: Optional[int] = None


@dataclass
class FriendInfo:
    """新增好友回调中的 ``friendInfo`` 字段。"""

    token: Optional[str] = None
    friendId: Optional[int] = None
    isFollow: Optional[int] = None
    nickName: Optional[str] = None
    havePhone: Optional[int] = None
    createTime: Optional[str] = None
    emailStatus: Optional[int] = None


@dataclass
class CallbackPayload:
    """PushPlus 回调统一载体。

    使用 ``CallbackParser.parse(json)`` 解析回调请求体后，根据 :attr:`event`
    判断事件类型并取对应的字段。
    """

    event: Optional[CallbackEvent] = None
    messageInfo: Optional[MessageCompleteInfo] = None
    topicUserInfo: Optional[TopicUserInfo] = None
    friendInfo: Optional[FriendInfo] = None
    qrCode: Optional[str] = None
    """自定义二维码参数（仅 ``add_friend`` 事件有值）。"""


__all__ = [
    "MessageCompleteInfo",
    "TopicUserInfo",
    "FriendInfo",
    "CallbackPayload",
]
