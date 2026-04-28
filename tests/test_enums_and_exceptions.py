"""枚举/异常基础行为校验。"""
from __future__ import annotations

from perk_pushplus import (
    CallbackEvent,
    Channel,
    ErrorCode,
    PushPlusError,
    SendStatus,
    Template,
    WebhookType,
)


def test_channel_of_case_insensitive():
    assert Channel.of("WeChat") is Channel.WECHAT
    assert Channel.of("clawbot") is Channel.CLAWBOT
    assert Channel.of(None) is None
    assert Channel.of("not-exist") is None


def test_template_codes():
    assert Template.HTML.value == "html"
    assert Template.MARKDOWN.code == "markdown"
    assert Template.CLOUD_MONITOR.value == "cloudMonitor"


def test_callback_event_message_complete_keep_typo():
    assert CallbackEvent.MESSAGE_COMPLETE.value == "message_complate"


def test_send_status_enum_descriptions():
    assert SendStatus.SUCCESS.description == "发送成功"
    assert SendStatus.FAILED.code == 3


def test_webhook_type_descriptions():
    assert WebhookType.WORK_WECHAT_BOT.description == "企业微信机器人"
    assert WebhookType.BARK.code == 50


def test_error_code_rate_limited():
    assert ErrorCode.is_rate_limited(900) is True
    assert ErrorCode.is_rate_limited(200) is False
    assert ErrorCode.from_code(900) is ErrorCode.RATE_LIMITED
    assert ErrorCode.from_code(None) is ErrorCode.UNKNOWN


def test_pushplus_error_exposes_metadata():
    exc = PushPlusError("rate", code=900)
    assert exc.code == 900
    assert exc.is_rate_limited() is True
    assert "code=900" in str(exc)
