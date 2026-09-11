"""开放接口 - 消息规则触发记录（文档「十四. 消息规则接口」第 10、11 节）。"""
from __future__ import annotations

from typing import Optional

from ..models import ForwardLogDetail, ForwardLogItem, ForwardLogListQuery, PageResult
from .base import OpenAbstractApi


class ForwardLogApi(OpenAbstractApi):
    """消息规则触发记录。"""

    def list(self, query: Optional[ForwardLogListQuery] = None) -> PageResult[ForwardLogItem]:
        body = query if query is not None else ForwardLogListQuery()
        result = self.execute_open(
            "POST", "/api/open/forwardLog/list", body, PageResult[ForwardLogItem]
        )
        return result or PageResult(list=[])

    def detail(self, log_id: int) -> ForwardLogDetail:
        path = self.append_query("/api/open/forwardLog/detail", {"logId": int(log_id)})
        return self.execute_open("GET", path, None, ForwardLogDetail)


__all__ = ["ForwardLogApi"]
