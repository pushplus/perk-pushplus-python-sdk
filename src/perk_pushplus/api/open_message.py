"""开放接口 - 消息接口（文档「二. 消息接口」）。"""
from __future__ import annotations

from typing import List

from ..exceptions import PushPlusError
from ..models import MessageItem, PageQuery, PageResult, SendMessageResult
from .base import OpenAbstractApi


class OpenMessageApi(OpenAbstractApi):
    """开放接口下的消息查询/删除等操作。"""

    def list(self, query: PageQuery = None) -> PageResult[MessageItem]:
        """1. 消息列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/message/list", body, PageResult[MessageItem]
        )
        return result or PageResult(list=[])

    def query_result(self, short_code: str) -> SendMessageResult:
        """2. 查询消息发送结果。"""

        if not short_code or not short_code.strip():
            raise PushPlusError("shortCode 不能为空")
        path = self.append_query(
            "/api/open/message/sendMessageResult", {"shortCode": short_code}
        )
        return self.execute_open("GET", path, None, SendMessageResult)

    def delete(self, short_code: str) -> str:
        """3. 删除消息。"""

        if not short_code or not short_code.strip():
            raise PushPlusError("shortCode 不能为空")
        path = self.append_query(
            "/api/open/message/deleteMessage", {"shortCode": short_code}
        )
        return self.execute_open("DELETE", path, None, str)

    def detail_url(self, short_code: str) -> str:
        """4. 消息详情 HTML 页面 URL（接口直接返回 HTML，本方法只拼装 URL）。"""

        if not short_code or not short_code.strip():
            raise PushPlusError("shortCode 不能为空")
        return self.resolve_url("/shortMessage/" + short_code)


__all__ = ["OpenMessageApi"]
