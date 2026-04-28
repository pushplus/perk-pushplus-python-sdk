"""开放接口 - 微信 ClawBot（文档「八. 微信ClawBot接口」）。"""
from __future__ import annotations

from typing import List

from ..models import ClawBotInfo, ClawBotMessage, ClawBotQrCode
from .base import OpenAbstractApi


class ClawBotApi(OpenAbstractApi):
    """微信 ClawBot 渠道相关接口。"""

    def get_bot_qrcode(self) -> ClawBotQrCode:
        """获取二维码。"""

        return self.execute_open(
            "GET", "/api/open/clawBot/getBotQrcode", None, ClawBotQrCode
        )

    def get_qrcode_status(self, qrcode: str) -> None:
        """扫码结果查询。"""

        path = self.append_query(
            "/api/open/clawBot/getQrcodeStatus", {"getQrcodeStatus": qrcode}
        )
        self.execute_open("GET", path, None, None)

    def bot_info(self) -> ClawBotInfo:
        """绑定详情。"""

        return self.execute_open(
            "GET", "/api/open/clawBot/botInfo", None, ClawBotInfo
        )

    def unbind(self) -> None:
        """解绑。"""

        self.execute_open("GET", "/api/open/clawBot/unbind", None, None)

    def get_msg(self) -> List[ClawBotMessage]:
        """获取发送消息。"""

        result = self.execute_open(
            "GET", "/api/open/clawBot/getMsg", None, List[ClawBotMessage]
        )
        return result or []


__all__ = ["ClawBotApi"]
