"""PushPlus SDK 枚举类型集合。

对应 Java SDK 中 ``com.perk.pushplus.enums`` 包下的全部枚举。
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class _StrCodeEnum(str, Enum):
    """字符串编码型枚举基类，Enum 实例的 ``value`` 即为对外 code。"""

    @classmethod
    def of(cls, code: Optional[str]):
        if code is None:
            return None
        for item in cls:
            if item.value.lower() == str(code).lower():
                return item
        return None


class Channel(_StrCodeEnum):
    """PushPlus 发送渠道。对应官方文档「发送渠道（channel）枚举」。"""

    WECHAT = "wechat"
    """微信公众号（默认）。"""
    WEBHOOK = "webhook"
    """第三方 webhook（企业微信/钉钉/飞书/bark/Gotify/Server酱/IFTTT/WxPusher 等）。"""
    CP = "cp"
    """企业微信应用。"""
    MAIL = "mail"
    """邮箱。"""
    SMS = "sms"
    """短信（收费）。"""
    VOICE = "voice"
    """语音（收费）。"""
    EXTENSION = "extension"
    """浏览器扩展插件 / 桌面应用程序。"""
    APP = "app"
    """App 渠道（安卓/鸿蒙/iOS）。"""
    CLAWBOT = "clawbot"
    """微信 ClawBot。"""

    @property
    def code(self) -> str:
        return self.value


class Template(_StrCodeEnum):
    """PushPlus 消息模板。"""

    HTML = "html"
    TXT = "txt"
    JSON = "json"
    MARKDOWN = "markdown"
    CLOUD_MONITOR = "cloudMonitor"
    JENKINS = "jenkins"
    ROUTE = "route"
    PAY = "pay"

    @property
    def code(self) -> str:
        return self.value


class CallbackEvent(_StrCodeEnum):
    """回调事件类型。"""

    MESSAGE_COMPLETE = "message_complate"
    """消息发送完成。注意官方拼写为 ``message_complate``。"""
    ADD_TOPIC_USER = "add_topic_user"
    """群组新增用户。"""
    ADD_FRIEND = "add_friend"
    """新增好友。"""

    @property
    def code(self) -> str:
        return self.value


class _IntCodeEnum(int, Enum):
    @classmethod
    def of(cls, code: Optional[int]):
        if code is None:
            return None
        try:
            value = int(code)
        except (TypeError, ValueError):
            return None
        for item in cls:
            if item.value == value:
                return item
        return None


class SendStatus(_IntCodeEnum):
    """消息投递状态。0-未发送，1-发送中，2-发送成功，3-发送失败。"""

    NOT_SENT = 0
    SENDING = 1
    SUCCESS = 2
    FAILED = 3

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _SEND_STATUS_DESCRIPTIONS[self]


_SEND_STATUS_DESCRIPTIONS = {
    SendStatus.NOT_SENT: "未发送",
    SendStatus.SENDING: "发送中",
    SendStatus.SUCCESS: "发送成功",
    SendStatus.FAILED: "发送失败",
}


class WebhookType(_IntCodeEnum):
    """Webhook 渠道类型。对应开放接口 ``webhookType`` 枚举值。"""

    WORK_WECHAT_BOT = 1
    DING_TALK_BOT = 2
    FEISHU_BOT = 3
    SERVER_CHAN = 4
    BARK = 50
    WORK_WECHAT_APP = 6
    TENCENT_LIGHT_LINK = 7
    IFTTT = 8
    JI_JIAN_YUN = 9
    GOTIFY = 10
    WX_PUSHER = 11
    CUSTOM = 12

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _WEBHOOK_TYPE_DESCRIPTIONS[self]


_WEBHOOK_TYPE_DESCRIPTIONS = {
    WebhookType.WORK_WECHAT_BOT: "企业微信机器人",
    WebhookType.DING_TALK_BOT: "钉钉机器人",
    WebhookType.FEISHU_BOT: "飞书机器人",
    WebhookType.SERVER_CHAN: "Server酱",
    WebhookType.BARK: "bark",
    WebhookType.WORK_WECHAT_APP: "企业微信应用",
    WebhookType.TENCENT_LIGHT_LINK: "腾讯轻联",
    WebhookType.IFTTT: "IFTTT",
    WebhookType.JI_JIAN_YUN: "集简云",
    WebhookType.GOTIFY: "Gotify",
    WebhookType.WX_PUSHER: "WxPusher",
    WebhookType.CUSTOM: "自定义",
}


class ErrorCode(_IntCodeEnum):
    """PushPlus 接口业务返回码语义。

    对应官方文档「接口返回码说明」：
    https://www.pushplus.plus/doc/guide/code.html
    """

    OK = 200
    NOT_LOGIN = 302
    UNAUTHORIZED = 401
    IP_FORBIDDEN = 403
    SERVER_ERROR = 500
    DATA_ERROR = 600
    FORBIDDEN_VIEW = 805
    INSUFFICIENT_POINTS = 888
    RATE_LIMITED = 900
    NOT_VERIFIED = 905
    INVALID_TOKEN = 903
    VALIDATION_ERROR = 999
    UNKNOWN = -1

    @property
    def code(self) -> int:
        return self.value

    @classmethod
    def from_code(cls, code: Optional[int]) -> "ErrorCode":
        if code is None:
            return cls.UNKNOWN
        try:
            value = int(code)
        except (TypeError, ValueError):
            return cls.UNKNOWN
        for item in cls:
            if item.value == value:
                return item
        return cls.UNKNOWN

    @staticmethod
    def is_rate_limited(code: Optional[int]) -> bool:
        return code is not None and int(code) == ErrorCode.RATE_LIMITED.value


__all__ = [
    "Channel",
    "Template",
    "CallbackEvent",
    "SendStatus",
    "WebhookType",
    "ErrorCode",
]
