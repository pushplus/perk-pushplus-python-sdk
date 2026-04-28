"""PushPlus SDK 统一异常。"""
from __future__ import annotations

from typing import Optional

from .enums import ErrorCode


class PushPlusError(Exception):
    """PushPlus SDK 统一运行时异常。

    在以下场景抛出：

    - HTTP 请求失败（网络异常、非 2xx 状态码）
    - PushPlus 业务接口返回 ``code != 200``
    - JSON 序列化/反序列化异常
    - SDK 参数校验失败
    - 本地限流守卫命中（``code=900`` 后被短路），不会真正发起 HTTP 请求
    """

    def __init__(
        self,
        message: str,
        code: int = -1,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self._message = message
        self._code = int(code) if code is not None else -1
        self.__cause__ = cause

    @property
    def code(self) -> int:
        """业务 code，HTTP 错误时为 HTTP 状态码，其他为 -1。"""

        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def error_code(self) -> ErrorCode:
        """把数值 code 映射为 :class:`ErrorCode` 枚举（未知为 ``UNKNOWN``）。"""

        return ErrorCode.from_code(self._code)

    def is_rate_limited(self) -> bool:
        """是否为 PushPlus 限流（``code=900``）。命中后建议当天停止继续调用发送消息接口。"""

        return ErrorCode.is_rate_limited(self._code)

    def __str__(self) -> str:  # noqa: D401
        return f"[code={self._code}] {self._message}"


# 兼容别名，与 Java 命名风格保持一致。
PushPlusException = PushPlusError


__all__ = ["PushPlusError", "PushPlusException"]
