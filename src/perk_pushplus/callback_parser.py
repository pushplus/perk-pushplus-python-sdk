"""PushPlus 回调请求体解析工具。

用法：在回调接口中拿到原始 JSON body，传入 :func:`parse` 即可。

示例（Flask）::

    @app.post("/pushplus/callback")
    def pushplus_callback():
        payload = parse(request.get_data(as_text=True))
        if payload.event == CallbackEvent.MESSAGE_COMPLETE:
            handle_message(payload.messageInfo)
        elif payload.event == CallbackEvent.ADD_TOPIC_USER:
            handle_subscriber(payload.topicUserInfo)
        elif payload.event == CallbackEvent.ADD_FRIEND:
            handle_friend(payload.friendInfo, payload.qrCode)
        return "ok"
"""
from __future__ import annotations

import json
from typing import Any, Optional

from .exceptions import PushPlusError
from .models import CallbackPayload
from .models.base import model_from_dict


def parse(json_body: str) -> CallbackPayload:
    """把 JSON 字符串解析为 :class:`CallbackPayload`。"""

    if json_body is None or json_body == "":
        raise PushPlusError("回调请求体为空")
    try:
        data = json.loads(json_body)
    except (TypeError, ValueError) as exc:
        raise PushPlusError(f"解析回调请求体失败: {exc}", cause=exc) from exc
    return parse_dict(data)


def parse_dict(data: Any) -> CallbackPayload:
    """从已解析为 dict 的回调内容构造 :class:`CallbackPayload`。"""

    if data is None:
        raise PushPlusError("回调请求体为空")
    payload: Optional[CallbackPayload] = model_from_dict(CallbackPayload, data)
    if payload is None:
        raise PushPlusError("回调请求体解析结果为空")
    return payload


__all__ = ["parse", "parse_dict"]
