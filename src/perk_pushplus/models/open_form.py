"""开放接口 - push 表单模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FormListQuery:
    """我的表单分页查询。官方结构是 ``{current, pageSize, params:{keyword, status}}``。"""

    current: Optional[int] = None
    pageSize: Optional[int] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def of(
        cls,
        current: Optional[int] = 1,
        page_size: Optional[int] = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> "FormListQuery":
        params: Dict[str, Any] = {}
        if keyword is not None:
            params["keyword"] = keyword
        if status is not None:
            params["status"] = status
        return cls(current=current, pageSize=page_size, params=params or None)


@dataclass
class FormCover:
    """表单封面页配置。"""

    enabled: Optional[bool] = None
    image: Optional[str] = None
    buttonText: Optional[str] = None


@dataclass
class FormTheme:
    """表单主题外观。"""

    primaryColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    headerImage: Optional[str] = None
    backgroundImage: Optional[str] = None
    cover: Optional[FormCover] = None


@dataclass
class FormSettings:
    """表单收集 / 展示设置。"""

    endTime: Optional[str] = None
    maxResponses: Optional[int] = None
    oncePerUser: Optional[bool] = None
    allowAnonymous: Optional[bool] = None
    password: Optional[str] = None
    showQuestionNumber: Optional[bool] = None
    onePerPage: Optional[bool] = None
    showPrevButton: Optional[bool] = None
    hideTitle: Optional[bool] = None
    hideCopyright: Optional[bool] = None
    hideAd: Optional[bool] = None
    showOutline: Optional[bool] = None
    thankText: Optional[str] = None
    redirectEnabled: Optional[bool] = None
    redirectUrl: Optional[str] = None
    allowEdit: Optional[bool] = None


@dataclass
class FormListItem:
    """表单列表项 / 创建、复制结果（不含题目明细）。"""

    id: Optional[int] = None
    formCode: Optional[str] = None
    fillUrl: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    responseCount: Optional[int] = None
    publishTime: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class FormSaveRequest:
    """保存表单设计。``items`` 为题目列表，每题至少含 id、type、label。"""

    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    theme: Optional[FormTheme] = None
    settings: Optional[FormSettings] = None


@dataclass
class FormDetail:
    """表单详情（含草稿题目、主题、设置）。"""

    id: Optional[int] = None
    formCode: Optional[str] = None
    fillUrl: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    theme: Optional[FormTheme] = None
    settings: Optional[FormSettings] = None
    status: Optional[int] = None
    publishDirty: Optional[bool] = None
    responseCount: Optional[int] = None
    publishTime: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class FormPublishDiff:
    """草稿题目与发布快照差异。"""

    dirty: Optional[bool] = None
    breaking: Optional[bool] = None
    responseCount: Optional[int] = None
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    typeChanged: List[str] = field(default_factory=list)
    optionChanged: List[str] = field(default_factory=list)


@dataclass
class FormPublishResult:
    """发布表单结果。"""

    id: Optional[int] = None
    formCode: Optional[str] = None
    fillUrl: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    previousStatus: Optional[int] = None
    publishDirty: Optional[bool] = None
    publishTime: Optional[str] = None


__all__ = [
    "FormListQuery",
    "FormCover",
    "FormTheme",
    "FormSettings",
    "FormListItem",
    "FormSaveRequest",
    "FormDetail",
    "FormPublishDiff",
    "FormPublishResult",
]
