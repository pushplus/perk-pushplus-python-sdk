"""开放接口 - 用户接口（文档「三. 用户接口」）。"""
from __future__ import annotations

from ..models import SendCount, UserInfo, UserLimitTime
from .base import OpenAbstractApi


class UserApi(OpenAbstractApi):
    """开放接口 - 用户相关。"""

    def get_token(self) -> str:
        """获取用户 token。"""

        return self.execute_open("GET", "/api/open/user/token", None, str)

    def my_info(self) -> UserInfo:
        """个人资料详情。"""

        return self.execute_open("GET", "/api/open/user/myInfo", None, UserInfo)

    def get_limit_time(self) -> UserLimitTime:
        """获取解封剩余时间。"""

        return self.execute_open(
            "GET", "/api/open/user/userLimitTime", None, UserLimitTime
        )

    def get_send_count(self) -> SendCount:
        """查询当日消息接口请求次数。"""

        return self.execute_open("GET", "/api/open/user/sendCount", None, SendCount)


__all__ = ["UserApi"]
