"""perk-pushplus-python-sdk 快速开始示例。

运行前请把 ``YOUR_TOKEN`` / ``YOUR_SECRET_KEY`` 改成自己在 PushPlus 个人中心
申请到的真实 token / secretKey。
"""
from __future__ import annotations

import logging

from perk_pushplus import (
    BatchSendRequest,
    CallbackEvent,
    Channel,
    PushPlusClient,
    PushPlusError,
    SendRequest,
    Template,
    callback_parser,
)


logging.basicConfig(level=logging.INFO)


def main() -> None:
    client = (
        PushPlusClient.builder()
        .token("YOUR_TOKEN")
        .secret_key("YOUR_SECRET_KEY")
        .log_request(True)
        .build()
    )

    try:
        sc = client.send_simple("测试", "<b>来自 Python SDK</b>")
        print("发送结果 shortCode:", sc)
    except PushPlusError as exc:
        print("发送失败:", exc)

    try:
        sc = client.send(
            SendRequest.builder()
            .title("CPU 告警")
            .content("# CPU > 90%\n请尽快处理")
            .template(Template.MARKDOWN)
            .channel(Channel.WECHAT)
            .build()
        )
        print("Markdown 发送结果:", sc)
    except PushPlusError as exc:
        print("Markdown 发送失败:", exc)

    try:
        results = client.batch_send(
            BatchSendRequest.builder()
            .title("多渠道告警")
            .content("CPU > 90%")
            .channel(Channel.WECHAT).option("")
            .channel(Channel.EXTENSION).option("")
            .build()
        )
        for r in results:
            print("渠道", r.channel, "shortCode", r.shortCode, "code", r.code)
    except PushPlusError as exc:
        print("多渠道发送失败:", exc)

    try:
        info = client.user.my_info()
        print("用户昵称:", info.nickName)
        page = client.open_message.list()
        print("消息总数:", page.total)
    except PushPlusError as exc:
        print("调用开放接口失败:", exc)


def demo_callback(raw_body: str) -> str:
    """模拟 web 框架收到 PushPlus 回调请求体后的处理。"""

    payload = callback_parser.parse(raw_body)
    if payload.event is CallbackEvent.MESSAGE_COMPLETE:
        info = payload.messageInfo
        print("[回调] 消息完成", info.shortCode, info.get_send_status_enum())
    elif payload.event is CallbackEvent.ADD_TOPIC_USER:
        print("[回调] 群组新增用户", payload.topicUserInfo.openId)
    elif payload.event is CallbackEvent.ADD_FRIEND:
        print("[回调] 新增好友", payload.friendInfo.token, payload.qrCode)
    return "ok"


if __name__ == "__main__":
    main()
