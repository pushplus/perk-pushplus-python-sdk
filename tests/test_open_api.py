"""开放接口的 access-key 注入与 401 自动重试逻辑测试。"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

import pytest

from perk_pushplus import (
    HttpResponse,
    PushPlusClient,
    PushPlusConfig,
    PushPlusError,
)


class ScriptedRequester:
    """根据请求 URL 路径返回预设响应。"""

    def __init__(self) -> None:
        self.calls: List[Tuple[str, str, Optional[Dict[str, str]], Optional[str]]] = []
        self.responses: List[Tuple[str, int, str]] = []
        # 默认对 getAccessKey 返回固定的 access key。
        self.access_keys: List[str] = ["ak-1"]

    def push(self, url_suffix: str, status: int, body: str) -> None:
        self.responses.append((url_suffix, status, body))

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[str],
    ) -> HttpResponse:
        self.calls.append((method, url, headers, body))
        if "/api/common/openApi/getAccessKey" in url:
            ak = self.access_keys.pop(0) if self.access_keys else "ak-default"
            payload = json.dumps(
                {
                    "code": 200,
                    "msg": "ok",
                    "data": {"accessKey": ak, "expiresIn": 7200},
                }
            )
            return HttpResponse(status_code=200, body=payload)
        if not self.responses:
            raise AssertionError(f"未配置响应: {url}")
        suffix, status, payload = self.responses.pop(0)
        if suffix not in url:
            raise AssertionError(
                f"期望调用 {suffix}，实际请求 {url}"
            )
        return HttpResponse(status_code=status, body=payload)


def _ok(data) -> str:
    return json.dumps({"code": 200, "msg": "ok", "data": data})


def _err(code: int, msg: str, data=None) -> str:
    return json.dumps({"code": code, "msg": msg, "data": data})


def _build_client(req: ScriptedRequester) -> PushPlusClient:
    return (
        PushPlusClient.builder()
        .token("user-token")
        .secret_key("secret")
        .http_requester(req)
        .build()
    )


def test_user_my_info_passes_access_key_header():
    req = ScriptedRequester()
    req.push(
        "/api/open/user/myInfo",
        200,
        _ok({"nickName": "陈大人", "openId": "oid", "headImgUrl": "https://x"}),
    )
    client = _build_client(req)
    info = client.user.my_info()
    assert info.nickName == "陈大人"
    headers = req.calls[1][2]  # 第 0 次是 getAccessKey
    assert headers and headers.get("access-key") == "ak-1"


def test_open_api_retries_after_401():
    req = ScriptedRequester()
    req.access_keys = ["ak-1", "ak-2"]
    req.push("/api/open/user/myInfo", 200, _err(401, "AccessKey 无效"))
    req.push(
        "/api/open/user/myInfo",
        200,
        _ok({"nickName": "陈大人"}),
    )
    client = _build_client(req)
    info = client.user.my_info()
    assert info.nickName == "陈大人"
    # 1) getAccessKey -> 2) myInfo (401) -> 3) getAccessKey (refresh) -> 4) myInfo (ok)
    assert len(req.calls) == 4
    assert req.calls[1][2]["access-key"] == "ak-1"
    assert req.calls[3][2]["access-key"] == "ak-2"


def test_open_api_business_error_raises():
    req = ScriptedRequester()
    req.push("/api/open/user/myInfo", 200, _err(500, "服务异常"))
    client = _build_client(req)
    with pytest.raises(PushPlusError) as exc:
        client.user.my_info()
    assert exc.value.code == 500


def test_open_message_list_returns_page_result():
    req = ScriptedRequester()
    req.push(
        "/api/open/message/list",
        200,
        _ok(
            {
                "pageNum": 1,
                "pageSize": 20,
                "total": 1,
                "pages": 1,
                "list": [
                    {
                        "title": "t1",
                        "shortCode": "sc1",
                        "channel": "wechat",
                        "messageType": 1,
                    }
                ],
            }
        ),
    )
    client = _build_client(req)
    page = client.open_message.list()
    assert page.total == 1
    assert page.list[0].shortCode == "sc1"


def test_open_message_detail_url():
    req = ScriptedRequester()
    client = _build_client(req)
    url = client.open_message.detail_url("abc123")
    assert url.endswith("/shortMessage/abc123")
