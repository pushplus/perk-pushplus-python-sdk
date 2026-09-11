"""开放接口 - 消息规则与触发记录模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ForwardConditionItem:
    """图形化触发条件中的单条比较。"""

    varName: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None


@dataclass
class ForwardCondition:
    """图形化触发条件。"""

    logic: Optional[str] = None
    items: Optional[List[ForwardConditionItem]] = None


@dataclass
class ForwardVariable:
    """模板变量。"""

    id: Optional[int] = None
    ruleId: Optional[int] = None
    varName: Optional[str] = None
    sourceType: Optional[int] = None
    """1-请求头，2-Query参数，3-请求体，4-URL路径，5-主题（邮件）。"""
    extractType: Optional[int] = None
    """1-序列化数据，2-正则表达式，3-JSONPath，4-原始全文。"""
    extractKey: Optional[str] = None
    defaultValue: Optional[str] = None
    sort: Optional[int] = None


@dataclass
class ForwardTarget:
    """发送目标。"""

    id: Optional[int] = None
    ruleId: Optional[int] = None
    channel: Optional[str] = None
    option: Optional[str] = None
    messageType: Optional[str] = None
    topic: Optional[str] = None
    to: Optional[str] = None
    sort: Optional[int] = None


@dataclass
class ForwardRuleItem:
    """消息规则列表项。"""

    id: Optional[int] = None
    tokenId: Optional[int] = None
    tokenName: Optional[str] = None
    ruleName: Optional[str] = None
    sourceType: Optional[int] = None
    sourceTypeName: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None
    conditionExpr: Optional[str] = None
    targetCount: Optional[int] = None
    createTime: Optional[str] = None


@dataclass
class ForwardRuleDetail:
    """消息规则详情。"""

    id: Optional[int] = None
    tokenId: Optional[int] = None
    ruleName: Optional[str] = None
    sourceType: Optional[int] = None
    status: Optional[int] = None
    sort: Optional[int] = None
    conditionExpr: Optional[str] = None
    condition: Optional[ForwardCondition] = None
    titleTemplate: Optional[str] = None
    contentTemplate: Optional[str] = None
    template: Optional[str] = None
    pre: Optional[str] = None
    stopOnMatch: Optional[int] = None
    limitPeriod: Optional[int] = None
    limitCount: Optional[int] = None
    activeStartTime: Optional[str] = None
    activeEndTime: Optional[str] = None
    activeWeekdays: Optional[str] = None
    remark: Optional[str] = None
    variables: Optional[List[ForwardVariable]] = None
    targets: Optional[List[ForwardTarget]] = None
    createTime: Optional[str] = None


@dataclass
class ForwardRuleSaveRequest:
    """新增 / 修改消息规则（修改时 ``id`` 必填）。"""

    ruleName: Optional[str] = None
    id: Optional[int] = None
    tokenId: Optional[int] = None
    sourceType: Optional[int] = None
    status: Optional[int] = None
    sort: Optional[int] = None
    condition: Optional[ForwardCondition] = None
    conditionExpr: Optional[str] = None
    titleTemplate: Optional[str] = None
    contentTemplate: Optional[str] = None
    template: Optional[str] = None
    pre: Optional[str] = None
    stopOnMatch: Optional[int] = None
    limitPeriod: Optional[int] = None
    limitCount: Optional[int] = None
    activeStartTime: Optional[str] = None
    activeEndTime: Optional[str] = None
    activeWeekdays: Optional[str] = None
    remark: Optional[str] = None
    variables: Optional[List[ForwardVariable]] = None
    targets: Optional[List[ForwardTarget]] = None


@dataclass
class ForwardRuleTestRequest:
    """测试消息规则请求。不会真正发送消息。"""

    sourceType: Optional[int] = None
    contentType: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    query: Optional[Dict[str, Any]] = None
    body: Optional[str] = None
    title: Optional[str] = None
    mailFrom: Optional[str] = None
    mailTo: Optional[str] = None
    mailCc: Optional[str] = None
    condition: Optional[ForwardCondition] = None
    conditionExpr: Optional[str] = None
    titleTemplate: Optional[str] = None
    contentTemplate: Optional[str] = None
    template: Optional[str] = None
    pre: Optional[str] = None
    variables: Optional[List[ForwardVariable]] = None


@dataclass
class ForwardRuleTestResult:
    """测试消息规则结果。"""

    variables: Optional[Dict[str, Any]] = None
    matched: Optional[bool] = None
    conditionExpr: Optional[str] = None
    errorMessage: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    template: Optional[str] = None


@dataclass
class ForwardRuleSetting:
    """消息规则总开关。"""

    mode: Optional[int] = None
    """0-关闭，1-开启且未命中仍推送，2-开启且未命中不推送。"""


@dataclass
class ForwardLogListQuery:
    """触发记录分页查询。官方结构是 ``{current, pageSize, params:{ruleId, matchResult}}``。"""

    current: Optional[int] = None
    pageSize: Optional[int] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def of(
        cls,
        current: Optional[int] = 1,
        page_size: Optional[int] = 20,
        rule_id: Optional[int] = None,
        match_result: Optional[int] = None,
    ) -> "ForwardLogListQuery":
        params: Dict[str, Any] = {}
        if rule_id is not None:
            params["ruleId"] = rule_id
        if match_result is not None:
            params["matchResult"] = match_result
        return cls(current=current, pageSize=page_size, params=params or None)


@dataclass
class ForwardLogItem:
    """触发记录列表项。"""

    id: Optional[int] = None
    ruleId: Optional[int] = None
    ruleName: Optional[str] = None
    sourceType: Optional[int] = None
    sourceTypeName: Optional[str] = None
    requestIp: Optional[str] = None
    matchResult: Optional[int] = None
    matchResultName: Optional[str] = None
    shortCodes: Optional[str] = None
    errorMessage: Optional[str] = None
    createTime: Optional[str] = None


@dataclass
class ForwardLogDetail:
    """触发记录详情。"""

    id: Optional[int] = None
    ruleId: Optional[int] = None
    ruleName: Optional[str] = None
    sourceType: Optional[int] = None
    sourceTypeName: Optional[str] = None
    requestIp: Optional[str] = None
    requestMethod: Optional[str] = None
    requestHeaders: Optional[str] = None
    requestQuery: Optional[str] = None
    requestBody: Optional[str] = None
    variables: Optional[str] = None
    matchResult: Optional[int] = None
    matchResultName: Optional[str] = None
    shortCodes: Optional[str] = None
    errorMessage: Optional[str] = None
    createTime: Optional[str] = None


__all__ = [
    "ForwardConditionItem",
    "ForwardCondition",
    "ForwardVariable",
    "ForwardTarget",
    "ForwardRuleItem",
    "ForwardRuleDetail",
    "ForwardRuleSaveRequest",
    "ForwardRuleTestRequest",
    "ForwardRuleTestResult",
    "ForwardRuleSetting",
    "ForwardLogListQuery",
    "ForwardLogItem",
    "ForwardLogDetail",
]
