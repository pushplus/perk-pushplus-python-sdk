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


def test_forward_rule_and_log():
    req = ScriptedRequester()
    req.push(
        "/api/open/forwardRule/list",
        200,
        _ok({"pageNum": 1, "list": [{"id": 1, "ruleName": "阿里云监控多渠道", "sourceType": 1}]}),
    )
    req.push("/api/open/forwardRule/add", 200, _ok(None))
    req.push(
        "/api/open/forwardRule/test",
        200,
        _ok({"matched": True, "title": "ECS-内存使用率", "conditionExpr": "alertState == 'ALERT'"}),
    )
    req.push("/api/open/forwardRule/setting?mode=1", 200, _ok(None))
    req.push("/api/open/forwardRule/setting", 200, _ok({"mode": 1}))
    req.push(
        "/api/open/forwardLog/list",
        200,
        _ok({"pageNum": 1, "list": [{"id": 9, "ruleId": 1, "matchResult": 1}]}),
    )
    req.push(
        "/api/open/forwardLog/detail",
        200,
        _ok({"id": 9, "ruleId": 1, "requestBody": '{"alertState":"ALERT"}'}),
    )
    client = _build_client(req)

    from perk_pushplus import (
        ForwardLogListQuery,
        ForwardRuleSaveRequest,
        ForwardRuleTestRequest,
        ForwardVariable,
    )

    page = client.forward_rule.list()
    assert page.list[0].ruleName == "阿里云监控多渠道"
    client.forward_rule.add(
        ForwardRuleSaveRequest(
            ruleName="阿里云监控多渠道",
            tokenId=-1,
            sourceType=1,
            variables=[ForwardVariable(varName="alertState", sourceType=3, extractType=1, extractKey="alertState")],
        )
    )
    tested = client.forward_rule.test(
        ForwardRuleTestRequest(sourceType=1, body='{"alertState":"ALERT"}', conditionExpr="alertState == 'ALERT'")
    )
    assert tested.matched is True
    client.forward_rule.save_setting(1)
    setting = client.forward_rule.get_setting()
    assert setting.mode == 1
    logs = client.forward_log.list(ForwardLogListQuery.of(1, 20, rule_id=1, match_result=1))
    assert logs.list[0].id == 9
    detail = client.forward_log.detail(9)
    assert "ALERT" in detail.requestBody

    add_call = next(c for c in req.calls if "/api/open/forwardRule/add" in c[1])
    assert json.loads(add_call[3])["tokenId"] == -1
    assert any("setting?mode=1" in c[1] for c in req.calls)
    log_list = next(c for c in req.calls if "/api/open/forwardLog/list" in c[1])
    assert json.loads(log_list[3])["params"]["matchResult"] == 1
    assert any("logId=9" in c[1] for c in req.calls)


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


def test_cmcc_bind_and_status():
    req = ScriptedRequester()
    req.push("/api/open/cmcc/bind", 200, _ok(None))
    req.push(
        "/api/open/cmcc/info",
        200,
        _ok({"bound": 1, "apiKeyMasked": "ak_***xxx", "createTime": "2026-09-14 10:20:00"}),
    )
    req.push("/api/open/cmcc/test", 200, _ok(None))
    req.push("/api/open/cmcc/unbind", 200, _ok(None))
    client = _build_client(req)

    client.cmcc.bind("ak_xxxxxxxxxxxxxxxx")
    bind_call = next(c for c in req.calls if "/api/open/cmcc/bind" in c[1])
    assert bind_call[2]["access-key"] == "ak-1"
    assert json.loads(bind_call[3])["apiKey"] == "ak_xxxxxxxxxxxxxxxx"

    info = client.cmcc.info()
    assert info.bound == 1
    assert info.apiKeyMasked == "ak_***xxx"

    client.cmcc.send_test()
    assert any("/api/open/cmcc/test" in c[1] for c in req.calls)

    client.cmcc.unbind()
    assert any("/api/open/cmcc/unbind" in c[1] for c in req.calls)


def test_qq_bot_bind_and_group_config():
    req = ScriptedRequester()
    req.push(
        "/api/open/qqBot/getBindLink",
        200,
        _ok({"url": "https://qun.qq.com/qunpro/robot/share?robot_appid=1", "bindCode": "A1B2C3", "expireSeconds": 300}),
    )
    req.push(
        "/api/open/qqBot/botInfo",
        200,
        _ok({"isBind": 1, "receiveStatus": 1, "botInfo": {"botAppId": "1", "username": "pushplus"}}),
    )
    req.push(
        "/api/open/qqBot/groupList",
        200,
        _ok([{"id": 9, "groupOpenId": "OPEN-1", "status": 1, "groupName": "运维告警群", "groupTags": ["运维"]}]),
    )
    req.push("/api/open/qqBot/add", 200, _ok(None))
    req.push(
        "/api/open/qqBot/list",
        200,
        _ok({"pageNum": 1, "pageSize": 20, "total": 1, "pages": 1, "list": [{"id": 3, "qqCode": "ops-group", "sendType": 2, "qqGroupId": 9}]}),
    )
    req.push("/api/open/qqBot/delete", 200, _ok(None))
    client = _build_client(req)

    from perk_pushplus import QqBotSaveRequest

    link = client.qq_bot.get_bind_link(refresh=True)
    assert link.bindCode == "A1B2C3"
    assert "refresh=true" in next(c for c in req.calls if "getBindLink" in c[1])[1]

    bind = client.qq_bot.bot_info()
    assert bind.isBind == 1
    assert bind.botInfo is not None and bind.botInfo.username == "pushplus"

    groups = client.qq_bot.group_list()
    assert groups[0].id == 9
    assert groups[0].groupTags == ["运维"]

    client.qq_bot.add(QqBotSaveRequest(qqName="运维告警群", qqCode="ops-group", qqGroupId=9))
    add_call = next(c for c in req.calls if "/api/open/qqBot/add" in c[1])
    assert add_call[2]["access-key"] == "ak-1"
    assert json.loads(add_call[3])["sendType"] == 2

    page = client.qq_bot.list()
    assert page.list[0].qqCode == "ops-group"

    client.qq_bot.delete(3)
    delete_call = next(c for c in req.calls if "/api/open/qqBot/delete" in c[1])
    assert delete_call[0] == "DELETE"
    assert "id=3" in delete_call[1]


def test_qq_bot_custom_bot():
    req = ScriptedRequester()
    req.push(
        "/api/open/qqBot/myBots",
        200,
        _ok({
            "bots": [
                {"botAppId": "1", "botType": 1, "isBind": 1, "isDefault": 1},
                {"botAppId": "102", "botType": 2, "isBind": 0},
            ],
            "customBotCount": 1,
            "customBotLimit": 5,
            "serverIps": ["1.2.3.4"],
        }),
    )
    req.push(
        "/api/open/qqBot/customBot/preview",
        200,
        _ok({"botAppId": "102", "username": "my-bot", "botType": 2}),
    )
    req.push("/api/open/qqBot/customBot/add", 200, _ok(None))
    req.push(
        "/api/open/qqBot/getBindLink",
        200,
        _ok({"bindCode": "A1B2C3", "botAppId": "102", "botType": 2}),
    )
    req.push("/api/open/qqBot/groupList", 200, _ok([]))
    req.push("/api/open/qqBot/setDefault", 200, _ok(None))
    req.push("/api/open/qqBot/add", 200, _ok(None))
    req.push("/api/open/qqBot/customBot/delete", 200, _ok(None))
    client = _build_client(req)

    from perk_pushplus import QqBotSaveRequest, QqCustomBotRequest
    from perk_pushplus.api.qqbot import SEND_TYPE_SELF

    mine = client.qq_bot.my_bots()
    assert len(mine.bots) == 2
    assert mine.bots[1].botType == 2
    assert mine.bots[1].botAppId == "102"
    assert mine.customBotLimit == 5
    assert mine.serverIps == ["1.2.3.4"]

    credential = QqCustomBotRequest(botAppId="102", appSecret="secret")
    preview = client.qq_bot.preview_custom_bot(credential)
    assert preview.username == "my-bot"
    assert preview.botAppId == "102"
    client.qq_bot.add_custom_bot(credential)
    add_bot_call = next(c for c in req.calls if "/api/open/qqBot/customBot/add" in c[1])
    assert json.loads(add_bot_call[3]) == {"botAppId": "102", "appSecret": "secret"}

    link = client.qq_bot.get_bind_link(bot_app_id="102")
    assert link.botType == 2
    link_url = next(c for c in req.calls if "getBindLink" in c[1])[1]
    assert "botAppId=102" in link_url
    assert "refresh" not in link_url

    client.qq_bot.group_list(bot_app_id="102")
    assert "botAppId=102" in next(c for c in req.calls if "groupList" in c[1])[1]

    client.qq_bot.set_default("102")
    assert "botAppId=102" in next(c for c in req.calls if "setDefault" in c[1])[1]

    client.qq_bot.add(QqBotSaveRequest(qqName="自有机器人私聊", qqCode="my-bot-self", sendType=SEND_TYPE_SELF, botAppId="102"))
    add_body = json.loads(next(c for c in req.calls if "/api/open/qqBot/add" in c[1])[3])
    assert add_body["sendType"] == 1
    assert add_body["botAppId"] == "102"

    client.qq_bot.delete_custom_bot("102")
    delete_call = next(c for c in req.calls if "customBot/delete" in c[1])
    assert delete_call[0] == "DELETE"
    assert "?botAppId=102" in delete_call[1]
