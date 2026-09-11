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
    QQ = "qq"
    """QQ 机器人；不带 option 发给自己，option 填配置编码则发到对应 QQ 群。"""

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
    FORM = "form"
    """表单格式模板；发送时需传 pushId（表单编码）。"""
    DOC = "doc"
    """文档格式模板（push 文档）；发送时需传 pushId。"""
    EXCEL = "excel"
    """表格格式模板（push 表格）；发送时需传 pushId。"""

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


class FormStatus(_IntCodeEnum):
    """push 表单状态。0-草稿，1-收集中，2-已停止。"""

    DRAFT = 0
    COLLECTING = 1
    STOPPED = 2

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _FORM_STATUS_DESCRIPTIONS[self]


_FORM_STATUS_DESCRIPTIONS = {
    FormStatus.DRAFT: "草稿",
    FormStatus.COLLECTING: "收集中",
    FormStatus.STOPPED: "已停止",
}


class SharePerm(_IntCodeEnum):
    """push 文档 / 表格分享权限。0-关闭，1-开启（仅可查看）。"""

    CLOSED = 0
    VIEW = 1

    @property
    def code(self) -> int:
        return self.value


class ShareLogin(_IntCodeEnum):
    """push 文档 / 表格打开分享页是否需要登录。0-免登录，1-需登录。"""

    ANONYMOUS = 0
    REQUIRED = 1

    @property
    def code(self) -> int:
        return self.value


class ForwardMode(_IntCodeEnum):
    """消息规则总开关。0-关闭，1-开启且未命中仍推送，2-开启且未命中不推送。"""

    OFF = 0
    ON_FALLBACK = 1
    ON_STRICT = 2

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _FORWARD_MODE_DESCRIPTIONS[self]


_FORWARD_MODE_DESCRIPTIONS = {
    ForwardMode.OFF: "关闭（推送与原来一致）",
    ForwardMode.ON_FALLBACK: "开启，未命中时仍按默认方式推送",
    ForwardMode.ON_STRICT: "开启，未命中时不推送",
}


class ForwardSourceType(_IntCodeEnum):
    """消息规则触发来源。0-全部，1-消息接口，2-邮件。"""

    ALL = 0
    API = 1
    MAIL = 2

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _FORWARD_SOURCE_TYPE_DESCRIPTIONS[self]


_FORWARD_SOURCE_TYPE_DESCRIPTIONS = {
    ForwardSourceType.ALL: "全部",
    ForwardSourceType.API: "消息接口",
    ForwardSourceType.MAIL: "邮件",
}


class ForwardVarSourceType(_IntCodeEnum):
    """模板变量来源。1-请求头，2-Query参数，3-请求体，4-URL路径，5-主题（邮件）。"""

    HEADER = 1
    QUERY = 2
    BODY = 3
    PATH = 4
    SUBJECT = 5

    @property
    def code(self) -> int:
        return self.value


class ForwardExtractType(_IntCodeEnum):
    """模板变量提取方式。1-序列化数据，2-正则表达式，3-JSONPath，4-原始全文。"""

    SERIALIZED = 1
    REGEX = 2
    JSON_PATH = 3
    RAW = 4

    @property
    def code(self) -> int:
        return self.value


class ForwardMatchResult(_IntCodeEnum):
    """触发记录匹配结果。0-条件不满足，1-已转发，2-频率限制，3-不在触发时间段，4-执行异常。"""

    NOT_MATCHED = 0
    FORWARDED = 1
    RATE_LIMITED = 2
    OUT_OF_TIME = 3
    ERROR = 4

    @property
    def code(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return _FORWARD_MATCH_RESULT_DESCRIPTIONS[self]


_FORWARD_MATCH_RESULT_DESCRIPTIONS = {
    ForwardMatchResult.NOT_MATCHED: "条件不满足",
    ForwardMatchResult.FORWARDED: "已转发",
    ForwardMatchResult.RATE_LIMITED: "频率限制",
    ForwardMatchResult.OUT_OF_TIME: "不在触发时间段",
    ForwardMatchResult.ERROR: "执行异常",
}


class ForwardConditionOperator(_StrCodeEnum):
    """图形化触发条件运算符。"""

    EQ = "eq"
    NE = "ne"
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    REGEX = "regex"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "notIn"
    EMPTY = "empty"
    NOT_EMPTY = "notEmpty"

    @property
    def code(self) -> str:
        return self.value


class ForwardMessageType(_StrCodeEnum):
    """消息规则发送目标的消息类型。也支持写成 ``{{变量名}}``。"""

    ONE = "one"
    TOPIC = "topic"
    FRIEND = "friend"

    @property
    def code(self) -> str:
        return self.value


__all__ = [
    "Channel",
    "Template",
    "CallbackEvent",
    "SendStatus",
    "WebhookType",
    "ErrorCode",
    "FormStatus",
    "SharePerm",
    "ShareLogin",
    "ForwardMode",
    "ForwardSourceType",
    "ForwardVarSourceType",
    "ForwardExtractType",
    "ForwardMatchResult",
    "ForwardConditionOperator",
    "ForwardMessageType",
]
