"""``MessageApi`` / 限流守卫 / 客户端组装测试。"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

import pytest

from perk_pushplus import (
    BatchSendRequest,
    Channel,
    HttpResponse,
    PushPlusClient,
    PushPlusConfig,
    PushPlusError,
    SendRequest,
    Template,
)
from perk_pushplus.api.message import MessageApi


class FakeRequester:
    """用于断言请求参数的极简 :class:`HttpRequester` 实现。"""

    def __init__(self, responses: List[Tuple[int, str]]) -> None:
        self._responses = list(responses)
        self.calls: List[Tuple[str, str, Optional[Dict[str, str]], Optional[str]]] = []

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[str],
    ) -> HttpResponse:
        self.calls.append((method, url, headers, body))
        if not self._responses:
            raise AssertionError("FakeRequester: 没有更多预设响应")
        status, payload = self._responses.pop(0)
        return HttpResponse(status_code=status, body=payload)


def _ok(data) -> str:
    return json.dumps({"code": 200, "msg": "ok", "data": data})


def _err(code: int, msg: str, data=None) -> str:
    return json.dumps({"code": code, "msg": msg, "data": data})


def test_send_simple_returns_short_code():
    cfg = PushPlusConfig(token="user-token")
    fake = FakeRequester([(200, _ok("short-code-1"))])
    api = MessageApi(cfg, fake)
    sc = api.send_simple("hello", "world")
    assert sc == "short-code-1"
    assert len(fake.calls) == 1
    method, url, headers, body = fake.calls[0]
    assert method == "POST"
    assert url.endswith("/send")
    payload = json.loads(body)
    assert payload["token"] == "user-token"
    assert payload["title"] == "hello"
    assert payload["content"] == "world"
    assert "channel" not in payload  # None 字段被剔除


def test_send_uses_request_token_when_provided():
    cfg = PushPlusConfig(token="default-token")
    fake = FakeRequester([(200, _ok("sc"))])
    api = MessageApi(cfg, fake)
    req = SendRequest(token="explicit", content="x")
    api.send(req)
    payload = json.loads(fake.calls[0][3])
    assert payload["token"] == "explicit"


def test_send_validates_content():
    api = MessageApi(PushPlusConfig(token="t"), FakeRequester([]))
    with pytest.raises(PushPlusError):
        api.send(SendRequest())


def test_send_requires_token_when_missing():
    api = MessageApi(PushPlusConfig(), FakeRequester([]))
    with pytest.raises(PushPlusError):
        api.send_simple("t", "c")


def test_send_business_error_raises():
    fake = FakeRequester([(200, _err(900, "请求次数过多"))])
    api = MessageApi(PushPlusConfig(token="t"), fake)
    with pytest.raises(PushPlusError) as exc_info:
        api.send_simple("t", "c")
    assert exc_info.value.code == 900
    assert exc_info.value.is_rate_limited()


def test_rate_limit_guard_blocks_subsequent_calls():
    cfg = PushPlusConfig(token="t", rate_limit_guard_enabled=True)
    fake = FakeRequester([(200, _err(900, "rate"))])
    api = MessageApi(cfg, fake)
    with pytest.raises(PushPlusError):
        api.send_simple("t", "c")
    assert api.rate_limit_guard.blocked_until("t") is not None
    with pytest.raises(PushPlusError) as exc_info:
        api.send_simple("t", "c")
    assert exc_info.value.code == 900
    # 守卫拒绝了第二次请求，FakeRequester 不应再被调用。
    assert len(fake.calls) == 1


def test_batch_send_returns_results_and_serializes_csv():
    fake = FakeRequester(
        [
            (
                200,
                _ok(
                    [
                        {
                            "shortCode": "a",
                            "code": 200,
                            "channel": "wechat",
                            "message": "ok",
                        },
                        {
                            "shortCode": "b",
                            "code": 200,
                            "channel": "webhook",
                            "message": "ok",
                        },
                    ]
                ),
            )
        ]
    )
    api = MessageApi(PushPlusConfig(token="t"), fake)
    req = (
        BatchSendRequest.builder()
        .title("t")
        .content("c")
        .channel(Channel.WECHAT)
        .option("")
        .channel(Channel.WEBHOOK)
        .option("bark")
        .build()
    )
    results = api.batch_send(req)
    assert [r.short_code if hasattr(r, "short_code") else r.shortCode for r in results] == ["a", "b"]
    payload = json.loads(fake.calls[0][3])
    assert payload["channel"] == "wechat,webhook"
    assert payload["option"] == ",bark"


def test_pushplus_client_builder_creates_apis():
    fake = FakeRequester([(200, _ok("sc"))])
    client = (
        PushPlusClient.builder()
        .token("user-token")
        .secret_key("secret")
        .http_requester(fake)
        .build()
    )
    assert client.message is not None
    assert client.user is not None
    assert client.send_simple("t", "c") == "sc"
