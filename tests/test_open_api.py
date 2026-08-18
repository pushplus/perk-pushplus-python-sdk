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

    def execute_raw(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[bytes],
    ) -> HttpResponse:
        text = None if body is None else body.decode("utf-8", errors="replace")
        return self.execute(method, url, headers, text)


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
        _ok(
            {
                "nickName": "陈大人",
                "openId": "oid",
                "headImgUrl": "https://x",
                "vipInfo": {"isVip": 1, "lastDay": "2026-12-31"},
                "verifyStatus": 1,
            }
        ),
    )
    client = _build_client(req)
    info = client.user.my_info()
    assert info.nickName == "陈大人"
    assert info.vipInfo is not None
    assert info.vipInfo.isVip == 1
    assert info.vipInfo.lastDay == "2026-12-31"
    assert info.verifyStatus == 1
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


def test_form_create_save_publish():
    req = ScriptedRequester()
    req.push("/push/api/open/form/create", 200, _ok({"id": 10001, "title": "用户满意度调查", "status": 0}))
    req.push("/push/api/open/form/save", 200, _ok(None))
    req.push(
        "/push/api/open/form/publish",
        200,
        _ok({"id": 10001, "formCode": "a1b2c3d4", "fillUrl": "https://www.pushplus.plus/push/form/a1b2c3d4", "status": 1}),
    )
    client = _build_client(req)
    created = client.form.create("用户满意度调查")
    assert created.id == 10001
    from perk_pushplus import FormSaveRequest

    client.form.save(FormSaveRequest(id=10001, title="用户满意度调查", items=[{"id": "q1", "type": "input"}]))
    published = client.form.publish(10001)
    assert published.formCode == "a1b2c3d4"
    assert any("/push/api/open/form/create" in c[1] for c in req.calls)
    save_call = next(c for c in req.calls if "/push/api/open/form/save" in c[1])
    assert save_call[2]["access-key"] == "ak-1"
    assert "q1" in save_call[3]
    publish_call = next(c for c in req.calls if "/push/api/open/form/publish" in c[1])
    assert "id=10001" in publish_call[1]


def test_doc_save_content_and_publish():
    req = ScriptedRequester()
    req.push("/push/api/open/doc/create", 200, _ok({"docCode": "Ab3xY7kP", "title": "本周工作同步"}))
    req.push("/push/api/open/doc/saveContent", 200, _ok({"docCode": "Ab3xY7kP", "publishDirty": True}))
    req.push("/push/api/open/doc/publish", 200, _ok({"docCode": "Ab3xY7kP", "published": True}))
    client = _build_client(req)
    doc = client.doc.create("本周工作同步")
    client.doc.save_content(doc.docCode, "<p>hello</p>")
    published = client.doc.publish(doc.docCode)
    assert published.published is True
    save_call = next(c for c in req.calls if "/push/api/open/doc/saveContent" in c[1])
    assert "<p>hello</p>" in save_call[3]


def test_excel_write_cells_and_save_object():
    req = ScriptedRequester()
    req.push("/push/api/open/excel/create", 200, _ok({"docCode": "Sh3xY7kP", "title": "销售日报"}))
    req.push("/push/api/open/excel/writeCells", 200, _ok({"docCode": "Sh3xY7kP", "publishDirty": True}))
    req.push("/push/api/open/excel/saveContent", 200, _ok({"docCode": "Sh3xY7kP", "publishDirty": True}))
    client = _build_client(req)
    sheet = client.excel.create("销售日报")
    client.excel.write_cells(sheet.docCode, "A2", [["2026-08-13", 12800]], "Sheet1")
    client.excel.save_content(sheet.docCode, {"sheetOrder": ["sheet-1"], "sheets": {}})
    write_call = next(c for c in req.calls if "/push/api/open/excel/writeCells" in c[1])
    body = json.loads(write_call[3])
    assert body["range"] == "A2"
    assert body["sheetName"] == "Sheet1"
    save_call = next(c for c in req.calls if "/push/api/open/excel/saveContent" in c[1])
    saved = json.loads(save_call[3])
    assert isinstance(saved["content"], str)
    assert json.loads(saved["content"])["sheetOrder"] == ["sheet-1"]


def test_friend_and_topic_user_blacklist():
    req = ScriptedRequester()
    req.push("/api/open/friend/addBlacklist", 200, _ok(None))
    req.push(
        "/api/open/friend/blacklistList",
        200,
        _ok({"pageNum": 1, "pageSize": 20, "total": 1, "pages": 1, "list": [{"id": 4, "friendId": 1322}]}),
    )
    req.push("/api/open/friend/removeBlacklist", 200, _ok(None))
    req.push("/api/open/topicUser/addBlacklist", 200, _ok(None))
    req.push(
        "/api/open/topicUser/blacklistList",
        200,
        _ok({"pageNum": 1, "list": [{"id": 1, "userId": 1322}]}),
    )
    req.push("/api/open/topicUser/removeBlacklist", 200, _ok(None))
    client = _build_client(req)
    client.friend.add_blacklist(1322)
    friends = client.friend.blacklist_list()
    assert friends.list[0].friendId == 1322
    client.friend.remove_blacklist(4)
    from perk_pushplus import TopicUserListQuery

    client.topic_user.add_blacklist(10)
    users = client.topic_user.blacklist_list(TopicUserListQuery.of(1, 20, 100))
    assert users.list[0].id == 1
    client.topic_user.remove_blacklist(1)
    assert any("friendId=1322" in c[1] for c in req.calls)
    topic_list = next(c for c in req.calls if "/api/open/topicUser/blacklistList" in c[1])
    assert json.loads(topic_list[3])["params"]["topicId"] == 100


def test_form_list_uses_current_and_params():
    req = ScriptedRequester()
    req.push("/push/api/open/form/list", 200, _ok({"pageNum": 1, "pageSize": 20, "total": 0, "list": []}))
    client = _build_client(req)
    from perk_pushplus import FormListQuery

    client.form.list(FormListQuery.of(1, 20, "满意度", 1))
    list_call = next(c for c in req.calls if "/push/api/open/form/list" in c[1])
    body = json.loads(list_call[3])
    assert body["current"] == 1
    assert body["params"]["keyword"] == "满意度"
    assert body["params"]["status"] == 1


def test_doc_import():
    req = ScriptedRequester()
    req.push("/push/api/open/doc/import", 200, _ok({"docCode": "Ab3xY7kP", "title": "本周工作同步"}))
    client = _build_client(req)

    imported = client.doc.import_word(b"hello", "本周工作同步.docx")
    assert imported.docCode == "Ab3xY7kP"
    import_call = next(c for c in req.calls if "/push/api/open/doc/import" in c[1])
    assert import_call[2]["Content-Type"].startswith("multipart/form-data; boundary=")


def test_excel_import():
    req = ScriptedRequester()
    req.push("/push/api/open/excel/import", 200, _ok({"docCode": "Sh3xY7kP", "title": "销售日报"}))
    client = _build_client(req)

    imported = client.excel.import_excel(b"xlsx", "销售日报.xlsx")
    assert imported.docCode == "Sh3xY7kP"
