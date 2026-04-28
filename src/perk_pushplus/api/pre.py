"""开放接口 - 预处理信息（文档「十一. 预处理信息接口」）。需开通会员。"""
from __future__ import annotations

from typing import Optional

from ..models import PageQuery, PageResult, PreDetail, PreItem, PreSaveRequest, PreTestRequest
from .base import OpenAbstractApi


class PreApi(OpenAbstractApi):
    """预处理信息（仅会员）。"""

    def list(self, query: Optional[PageQuery] = None) -> PageResult[PreItem]:
        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/pre/list", body, PageResult[PreItem]
        )
        return result or PageResult(list=[])

    def detail(self, pre_id: int) -> PreDetail:
        path = self.append_query("/api/open/pre/detail", {"preId": int(pre_id)})
        return self.execute_open("GET", path, None, PreDetail)

    def add(self, req: PreSaveRequest) -> int:
        return self.execute_open("POST", "/api/open/pre/add", req, int)

    def edit(self, req: PreSaveRequest) -> str:
        return self.execute_open("POST", "/api/open/pre/edit", req, str)

    def delete(self, pre_id: int) -> str:
        path = self.append_query("/api/open/pre/delete", {"preId": int(pre_id)})
        return self.execute_open("DELETE", path, None, str)

    def test(self, req: PreTestRequest) -> str:
        """测试预处理代码，返回处理后的消息。"""

        return self.execute_open("POST", "/api/open/pre/test", req, str)


__all__ = ["PreApi"]
