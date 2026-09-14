"""开放接口 - 新消息 ClawBot（文档「九. 新消息ClawBot接口」）。

需先在手机 5G 消息的「新消息ClawBot」应用号中获取 Channel API Key，再调用绑定接口。
发送消息时 channel 传 ``cmcc``。仅支持中国移动用户。
"""
from __future__ import annotations

from ..models import CmccBindRequest, CmccInfo
from .base import OpenAbstractApi


class CmccApi(OpenAbstractApi):
    """新消息 ClawBot 渠道相关接口。"""

    def bind(self, api_key: str) -> None:
        """绑定新消息 ClawBot。``api_key`` 必须以 ``ak_`` 或 ``app_`` 开头。"""

        self.execute_open(
            "POST", "/api/open/cmcc/bind", CmccBindRequest(apiKey=api_key), None
        )

    def info(self) -> CmccInfo:
        """查询绑定状态。"""

        return self.execute_open("GET", "/api/open/cmcc/info", None, CmccInfo)

    def unbind(self) -> None:
        """解绑新消息 ClawBot。"""

        self.execute_open("GET", "/api/open/cmcc/unbind", None, None)

    def send_test(self) -> None:
        """发送测试消息。未绑定会返回「未绑定新消息ClawBot」。"""

        self.execute_open("GET", "/api/open/cmcc/test", None, None)


__all__ = ["CmccApi"]
