"""开放接口 - push 文档 / 表格共用模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocListQuery:
    """文档 / 表格分页查询。"""

    pageNum: Optional[int] = None
    pageSize: Optional[int] = None
    keyword: Optional[str] = None
    shareEnabled: Optional[bool] = None

    @classmethod
    def of(
        cls,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 10,
        keyword: Optional[str] = None,
        share_enabled: Optional[bool] = None,
    ) -> "DocListQuery":
        return cls(
            pageNum=page_num,
            pageSize=page_size,
            keyword=keyword,
            shareEnabled=share_enabled,
        )


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
