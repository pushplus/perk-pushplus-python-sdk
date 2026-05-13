"""perk-pushplus-python-sdk: PushPlus 推送加官方接口的 Python SDK。

提供消息接口（``/send``、``/batchSend``）以及全部开放接口的封装，
内置 AccessKey 自动管理与本地限流守卫。

参考文档：
- 消息接口：https://www.pushplus.plus/doc/guide/api.html
- 开放接口：https://www.pushplus.plus/doc/guide/openApi.html

快速使用::

    from perk_pushplus import PushPlusClient

    client = PushPlusClient.builder() \
        .token("your_user_token") \
        .secret_key("your_secret_key") \
        .build()

    short_code = client.send_simple("标题", "内容")
"""
from __future__ import annotations

from . import callback_parser
from .access_key import AccessKeyManager
from .client import PushPlusClient, PushPlusClientBuilder
from .config import DEFAULT_BASE_URL, PushPlusConfig
from .enums import (
    CallbackEvent,
    Channel,
    ErrorCode,
    SendStatus,
    Template,
    WebhookType,
)
from .exceptions import PushPlusError, PushPlusException
from .http import HttpRequester, HttpResponse, RequestsHttpRequester
from .models import (
    AccessKeyResult,
    ApiResponse,
    BatchSendRequest,
    BatchSendResult,
    CallbackFriendInfo,
    CallbackPayload,
    ClawBotInfo,
    ClawBotMessage,
    ClawBotQrCode,
    CpItem,
    FriendItem,
    FriendQrCode,
    ImageItem,
    ImageUploadResult,
    ImageUploadToken,
    MailDetail,
    MailItem,
    MessageCompleteInfo,
    MessageItem,
    MessageTokenAddRequest,
    MessageTokenEditRequest,
    MessageTokenItem,
    MessageTokenOption,
    MpItem,
    PageQuery,
    PageResult,
    PreDetail,
    PreItem,
    PreSaveRequest,
    PreTestRequest,
    SendCount,
    SendMessageResult,
    SendRequest,
    TopicAddRequest,
    TopicDetail,
    TopicEditRequest,
    TopicItem,
    TopicListQuery,
    TopicQrCode,
    TopicUserInfo,
    TopicUserItem,
    TopicUserListQuery,
    UserDefaultDetail,
    UserDefaultItem,
    UserDefaultSaveRequest,
    UserInfo,
    UserLimitTime,
    WebhookItem,
    WebhookSaveRequest,
)
from .rate_limit import RateLimitGuard

__version__ = "1.0.1"

__all__ = [
    "__version__",
    "PushPlusClient",
    "PushPlusClientBuilder",
    "PushPlusConfig",
    "DEFAULT_BASE_URL",
    "PushPlusError",
    "PushPlusException",
    "AccessKeyManager",
    "RateLimitGuard",
    "HttpRequester",
    "HttpResponse",
    "RequestsHttpRequester",
    "callback_parser",
    "Channel",
    "Template",
    "CallbackEvent",
    "SendStatus",
    "WebhookType",
    "ErrorCode",
    "ApiResponse",
    "PageQuery",
    "PageResult",
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
    "ImageUploadToken",
    "ImageUploadResult",
    "ImageItem",
]
