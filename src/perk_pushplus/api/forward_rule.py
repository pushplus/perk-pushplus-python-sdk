"""开放接口 - 消息规则（文档「十四. 消息规则接口」）。需开通会员后才能开启。"""
from __future__ import annotations

from typing import Optional

from ..models import (
    ForwardRuleDetail,
    ForwardRuleItem,
    ForwardRuleSaveRequest,
    ForwardRuleSetting,
    ForwardRuleTestRequest,
    ForwardRuleTestResult,
    PageQuery,
    PageResult,
)
from .base import OpenAbstractApi


class ForwardRuleApi(OpenAbstractApi):
    """消息规则（仅会员）。"""

    def list(self, query: Optional[PageQuery] = None) -> PageResult[ForwardRuleItem]:
        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/forwardRule/list", body, PageResult[ForwardRuleItem]
        )
        return result or PageResult(list=[])

    def detail(self, rule_id: int) -> ForwardRuleDetail:
        path = self.append_query("/api/open/forwardRule/detail", {"ruleId": int(rule_id)})
        return self.execute_open("GET", path, None, ForwardRuleDetail)

    def add(self, req: ForwardRuleSaveRequest) -> None:
        self.execute_open("POST", "/api/open/forwardRule/add", req, None)

    def edit(self, req: ForwardRuleSaveRequest) -> None:
        """修改消息规则；会整体覆盖模板变量和发送目标。"""

        self.execute_open("POST", "/api/open/forwardRule/edit", req, None)

    def delete(self, rule_id: int) -> None:
        path = self.append_query("/api/open/forwardRule/delete", {"ruleId": int(rule_id)})
        self.execute_open("DELETE", path, None, None)

    def change_status(self, rule_id: int, status: int) -> None:
        """启用 / 停用消息规则：1 启用，0 停用。"""

        path = self.append_query(
            "/api/open/forwardRule/changeStatus",
            {"ruleId": int(rule_id), "status": int(status)},
        )
        self.execute_open("GET", path, None, None)

    def test(self, req: ForwardRuleTestRequest) -> ForwardRuleTestResult:
        """用模拟请求测试规则，不会真正发送消息。"""

        return self.execute_open("POST", "/api/open/forwardRule/test", req, ForwardRuleTestResult)

    def get_setting(self) -> ForwardRuleSetting:
        return self.execute_open("GET", "/api/open/forwardRule/setting", None, ForwardRuleSetting)

    def save_setting(self, mode: int) -> None:
        """设置总开关：0 关闭，1 开启且未命中仍推送，2 开启且未命中不推送。"""

        path = self.append_query("/api/open/forwardRule/setting", {"mode": int(mode)})
        self.execute_open("GET", path, None, None)


__all__ = ["ForwardRuleApi"]
