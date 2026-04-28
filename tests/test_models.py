"""模型序列化/反序列化测试。"""
from __future__ import annotations

import json

from perk_pushplus import (
    BatchSendRequest,
    BatchSendResult,
    CallbackEvent,
    CallbackPayload,
    Channel,
    MessageItem,
    PageQuery,
    PageResult,
    SendRequest,
    Template,
    callback_parser,
)
from perk_pushplus.models.base import model_from_dict, model_to_dict


def test_send_request_builder_drops_none_on_serialize():
    req = (
        SendRequest.builder()
        .token("tk")
        .title("标题")
        .content("hi")
        .channel(Channel.WECHAT)
        .template(Template.HTML)
        .build()
    )
    payload = model_to_dict(req)
    assert payload == {
        "token": "tk",
        "title": "标题",
        "content": "hi",
        "template": "html",
        "channel": "wechat",
    }


def test_batch_send_builder_concats_channel_and_option():
    req = (
        BatchSendRequest.builder()
        .token("tk")
        .title("多渠道")
        .content("c")
        .channel(Channel.WECHAT)
        .option("")
        .channel(Channel.WEBHOOK)
        .option("bark")
        .channel(Channel.EXTENSION)
        .option("")
        .build()
    )
    assert req.channel == "wechat,webhook,extension"
    assert req.option == ",bark,"
    payload = model_to_dict(req)
    assert payload["channel"] == "wechat,webhook,extension"
    assert payload["option"] == ",bark,"


def test_model_from_dict_handles_generic_page_result():
    data = {
        "pageNum": 1,
        "pageSize": 20,
        "total": 2,
        "pages": 1,
        "list": [
            {
                "title": "t1",
                "shortCode": "sc1",
                "channel": "wechat",
                "messageType": 1,
                "updateTime": "2025-01-01",
            },
            {
                "title": "t2",
                "shortCode": "sc2",
                "channel": "webhook",
                "messageType": 2,
                "updateTime": "2025-01-02",
            },
        ],
    }
    result: PageResult[MessageItem] = model_from_dict(PageResult[MessageItem], data)
    assert result.total == 2
    assert len(result.list) == 2
    assert isinstance(result.list[0], MessageItem)
    assert result.list[0].channel is Channel.WECHAT
    assert result.list[1].channel is Channel.WEBHOOK


def test_batch_send_result_channel_enum_round_trip():
    items = model_from_dict(
        list,  # 退化路径
        [
            {"shortCode": "sc1", "code": 200, "channel": "wechat", "message": "ok"},
        ],
    )
    assert isinstance(items, list)


def test_batch_send_result_channel_via_typed_helper():
    from typing import List

    items = model_from_dict(
        List[BatchSendResult],
        [
            {"shortCode": "sc1", "code": 200, "channel": "wechat", "message": "ok"},
            {"shortCode": "sc2", "code": 200, "channel": "webhook", "message": "ok"},
        ],
    )
    assert len(items) == 2
    assert items[0].channel is Channel.WECHAT
    assert items[1].channel is Channel.WEBHOOK


def test_callback_parser_message_complete():
    body = json.dumps(
        {
            "event": "message_complate",
            "messageInfo": {
                "shortCode": "sc1",
                "sendStatus": 2,
                "message": "",
            },
        }
    )
    payload: CallbackPayload = callback_parser.parse(body)
    assert payload.event is CallbackEvent.MESSAGE_COMPLETE
    assert payload.messageInfo is not None
    assert payload.messageInfo.shortCode == "sc1"
    assert payload.messageInfo.get_send_status_enum().value == 2


def test_callback_parser_add_friend():
    body = json.dumps(
        {
            "event": "add_friend",
            "qrCode": "promo-2026",
            "friendInfo": {
                "token": "abc",
                "friendId": 5,
                "isFollow": 1,
                "havePhone": 0,
            },
        }
    )
    payload: CallbackPayload = callback_parser.parse(body)
    assert payload.event is CallbackEvent.ADD_FRIEND
    assert payload.qrCode == "promo-2026"
    assert payload.friendInfo is not None
    assert payload.friendInfo.friendId == 5


def test_page_query_of():
    q = PageQuery.of(2, 50)
    assert q.current == 2
    assert q.pageSize == 50
