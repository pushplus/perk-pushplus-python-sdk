"""PushPlus SDK 数据模型集合。

为了与 Java SDK 保持一致，所有请求/响应实体都定义为 :mod:`dataclasses`。
"""
from __future__ import annotations

from .base import ApiResponse, PageQuery, PageResult, model_to_dict, model_from_dict
from .send import BatchSendRequest, BatchSendResult, SendRequest
from .callback import (
    CallbackPayload,
    FriendInfo as CallbackFriendInfo,
    MessageCompleteInfo,
    TopicUserInfo,
)
from .open_access import AccessKeyResult
from .open_message import MessageItem, SendMessageResult
from .open_user import SendCount, UserInfo, UserLimitTime
from .open_token import (
    MessageTokenAddRequest,
    MessageTokenEditRequest,
    MessageTokenItem,
    MessageTokenOption,
)
from .open_topic import (
    TopicAddRequest,
    TopicDetail,
    TopicEditRequest,
    TopicItem,
    TopicListQuery,
    TopicQrCode,
    TopicUserItem,
    TopicUserListQuery,
)
from .open_friend import FriendItem, FriendQrCode
from .open_webhook import WebhookItem, WebhookSaveRequest
from .open_channel import CpItem, MailDetail, MailItem, MpItem
from .open_clawbot import ClawBotInfo, ClawBotMessage, ClawBotQrCode
from .open_setting import UserDefaultDetail, UserDefaultItem, UserDefaultSaveRequest
from .open_pre import PreDetail, PreItem, PreSaveRequest, PreTestRequest

__all__ = [
    "ApiResponse",
    "PageQuery",
    "PageResult",
    "model_to_dict",
    "model_from_dict",
    "SendRequest",
    "BatchSendRequest",
    "BatchSendResult",
    "CallbackPayload",
    "MessageCompleteInfo",
    "TopicUserInfo",
    "CallbackFriendInfo",
    "AccessKeyResult",
    "MessageItem",
    "SendMessageResult",
    "UserInfo",
    "UserLimitTime",
    "SendCount",
    "MessageTokenItem",
    "MessageTokenOption",
    "MessageTokenAddRequest",
    "MessageTokenEditRequest",
    "TopicItem",
    "TopicDetail",
    "TopicQrCode",
    "TopicListQuery",
    "TopicUserListQuery",
    "TopicUserItem",
    "TopicAddRequest",
    "TopicEditRequest",
    "FriendItem",
    "FriendQrCode",
    "WebhookItem",
    "WebhookSaveRequest",
    "MpItem",
    "CpItem",
    "MailItem",
    "MailDetail",
    "ClawBotQrCode",
    "ClawBotInfo",
    "ClawBotMessage",
    "UserDefaultItem",
    "UserDefaultDetail",
    "UserDefaultSaveRequest",
    "PreItem",
    "PreDetail",
    "PreSaveRequest",
    "PreTestRequest",
]
