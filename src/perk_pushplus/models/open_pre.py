"""开放接口 - 预处理信息模型（仅会员可用）。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PreItem:
    """预处理信息列表项。"""

    id: Optional[int] = None
    preName: Optional[str] = None
    preCode: Optional[str] = None
    contentType: Optional[int] = None
    """1-JavaScript。"""
    createTime: Optional[str] = None


@dataclass
class PreDetail:
    """预处理信息详情。"""

    id: Optional[int] = None
    preName: Optional[str] = None
    preCode: Optional[str] = None
    contentType: Optional[int] = None
    content: Optional[str] = None


@dataclass
class PreSaveRequest:
    """新增/修改预处理信息（修改时 ``id`` 必填）。"""

    id: Optional[int] = None
    content: Optional[str] = None
    preName: Optional[str] = None
    preCode: Optional[str] = None
    contentType: Optional[int] = None


@dataclass
class PreTestRequest:
    """测试预处理代码请求。"""

    content: Optional[str] = None
    contentType: Optional[int] = None
    message: Optional[str] = None


__all__ = ["PreItem", "PreDetail", "PreSaveRequest", "PreTestRequest"]
