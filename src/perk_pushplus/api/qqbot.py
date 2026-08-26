"""开放接口 - QQ 机器人（文档「九. QQ机器人接口」）。"""
from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

from ..models import (
    PageQuery,
    PageResult,
    QqBotBindInfo,
    QqBotBindLink,
    QqBotItem,
    QqBotSaveRequest,
    QqGroupItem,
)
from .base import OpenAbstractApi

SEND_TYPE_QQ_GROUP = 2
"""发送到 QQ 群，目前渠道配置仅支持该类型。"""


class QqBotApi(OpenAbstractApi):
    """QQ 机器人绑定与渠道配置相关接口。"""

    def get_bind_link(self, refresh: bool = False) -> QqBotBindLink:
        """获取绑定链接与绑定码；``refresh=True`` 时旧绑定码失效并重新生成。"""

        path = "/api/open/qqBot/getBindLink"
        if refresh:
            path = self.append_query(path, {"refresh": "true"})
        return self.execute_open("GET", path, None, QqBotBindLink)

    def bot_info(self) -> QqBotBindInfo:
        """查询绑定状态。"""

        return self.execute_open(
            "GET", "/api/open/qqBot/botInfo", None, QqBotBindInfo
        )

    def unbind(self) -> None:
        """解绑 QQ 机器人。"""

        self.execute_open("GET", "/api/open/qqBot/unbind", None, None)

    def group_list(self) -> List[QqGroupItem]:
        """获取机器人已加入的 QQ 群列表。"""

        result = self.execute_open(
            "GET", "/api/open/qqBot/groupList", None, List[QqGroupItem]
        )
        return result or []

    def list(self, query: Optional[PageQuery] = None) -> PageResult[QqBotItem]:
        """获取 QQ 机器人渠道配置列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/qqBot/list", body, PageResult[QqBotItem]
        )
        return result or PageResult(list=[])

    def add(self, request: QqBotSaveRequest) -> None:
        """新增渠道配置，用于把消息发送到指定 QQ 群；发给自己无需创建配置。"""

        self.execute_open(
            "POST", "/api/open/qqBot/add", _with_default_send_type(request), None
        )

    def edit(self, request: QqBotSaveRequest) -> None:
        """修改渠道配置；配置编码不可修改。"""

        self.execute_open(
            "POST", "/api/open/qqBot/edit", _with_default_send_type(request), None
        )

    def delete(self, config_id: int) -> None:
        """删除渠道配置。"""

        path = self.append_query("/api/open/qqBot/delete", {"id": int(config_id)})
        self.execute_open("DELETE", path, None, None)


def _with_default_send_type(request: QqBotSaveRequest) -> QqBotSaveRequest:
    if request is None or request.sendType is not None:
        return request
    return replace(request, sendType=SEND_TYPE_QQ_GROUP)


__all__ = ["QqBotApi", "SEND_TYPE_QQ_GROUP"]
