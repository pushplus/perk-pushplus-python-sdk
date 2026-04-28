"""开放接口 - 消息 token（文档「四. 消息token接口」）。"""
from __future__ import annotations

from typing import List, Optional

from ..models import (
    MessageTokenAddRequest,
    MessageTokenEditRequest,
    MessageTokenItem,
    MessageTokenOption,
    PageQuery,
    PageResult,
)
from .base import OpenAbstractApi


class MessageTokenApi(OpenAbstractApi):
    """消息 token 管理。"""

    def list(self, query: Optional[PageQuery] = None) -> PageResult[MessageTokenItem]:
        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/token/list", body, PageResult[MessageTokenItem]
        )
        return result or PageResult(list=[])

    def add(self, req: MessageTokenAddRequest) -> str:
        """新增消息 token，返回新建的 token 字符串。"""

        return self.execute_open("POST", "/api/open/token/add", req, str)

    def edit(self, req: MessageTokenEditRequest) -> str:
        return self.execute_open("POST", "/api/open/token/edit", req, str)

    def delete(self, token_id: int) -> str:
        path = self.append_query("/api/open/token/deleteToken", {"id": int(token_id)})
        return self.execute_open("DELETE", path, None, str)

    def select_list(self, type_: Optional[int] = 0) -> List[MessageTokenOption]:
        """消息 token 下拉选择列表。

        ``type_`` 为 0 时返回全部，1 时返回未配置默认推送渠道的消息 token。
        """

        path = self.append_query(
            "/api/open/token/selectTokenList", {"type": 0 if type_ is None else int(type_)}
        )
        result = self.execute_open("GET", path, None, List[MessageTokenOption])
        return result or []


__all__ = ["MessageTokenApi"]
