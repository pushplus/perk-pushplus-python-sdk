"""开放接口 - push 文档 / 表格共用模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DocListQuery:
    """文档 / 表格分页查询。官方结构是 ``{current, pageSize, params:{keyword, shareEnabled}}``。"""

    current: Optional[int] = None
    pageSize: Optional[int] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def of(
        cls,
        current: Optional[int] = 1,
        page_size: Optional[int] = 20,
        keyword: Optional[str] = None,
        share_enabled: Optional[bool] = None,
    ) -> "DocListQuery":
        params: Dict[str, Any] = {}
        if keyword is not None:
            params["keyword"] = keyword
        if share_enabled is not None:
            params["shareEnabled"] = share_enabled
        return cls(current=current, pageSize=page_size, params=params or None)


@dataclass
class DocListItem:
    """文档 / 表格列表项。"""

    docCode: Optional[str] = None
    shareUrl: Optional[str] = None
    title: Optional[str] = None
    sharePerm: Optional[int] = None
    shareLogin: Optional[int] = None
    perm: Optional[int] = None
    published: Optional[bool] = None
    publishTime: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class DocVo:
    """文档信息（不含正文）。"""

    docCode: Optional[str] = None
    shareUrl: Optional[str] = None
    title: Optional[str] = None
    sharePerm: Optional[int] = None
    shareLogin: Optional[int] = None
    perm: Optional[int] = None
    published: Optional[bool] = None
    publishDirty: Optional[bool] = None
    publishTime: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class DocContent(DocVo):
    """文档内容（HTML 草稿）。"""

    content: Optional[str] = None


@dataclass
class ExcelVo:
    """表格信息（不含正文）。"""

    docCode: Optional[str] = None
    shareUrl: Optional[str] = None
    title: Optional[str] = None
    sharePerm: Optional[int] = None
    shareLogin: Optional[int] = None
    perm: Optional[int] = None
    published: Optional[bool] = None
    publishDirty: Optional[bool] = None
    publishTime: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class ExcelContent(ExcelVo):
    """表格内容（整表 JSON 字符串草稿）。"""

    content: Optional[str] = None


__all__ = [
    "DocListQuery",
    "DocListItem",
    "DocVo",
    "DocContent",
    "ExcelVo",
    "ExcelContent",
]
