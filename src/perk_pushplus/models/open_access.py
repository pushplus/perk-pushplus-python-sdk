"""开放接口 - 获取 AccessKey 模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AccessKeyResult:
    """获取 AccessKey 接口响应。"""

    accessKey: Optional[str] = None
    """访问令牌，后续请求需加到 header 中。"""
    expiresIn: Optional[int] = None
    """过期时间（单位秒）。"""


__all__ = ["AccessKeyResult"]
