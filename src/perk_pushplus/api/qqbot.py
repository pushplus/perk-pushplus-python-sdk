"""开放接口 - QQ 机器人（文档「十. QQ机器人接口」）。

除 pushplus 官方机器人外，用户还可以添加自有机器人；带 ``bot_app_id`` 参数的方法用于指定要操作的机器人，
不传时按官方/默认机器人处理。
"""
from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

from ..models import (
    PageQuery,
    PageResult,
    QqBotBindInfo,
    QqBotBindLink,
    QqBotInfo,
    QqBotItem,
    QqBotSaveRequest,
    QqCustomBotRequest,
    QqGroupItem,
    QqMyBotList,
)
from .base import OpenAbstractApi

SEND_TYPE_SELF = 1
"""渠道配置发送类型：发给自己（需指定 ``botAppId``）。"""

SEND_TYPE_QQ_GROUP = 2
"""渠道配置发送类型：发送到 QQ 群，未指定 ``sendType`` 时的默认值。"""


class QqBotApi(OpenAbstractApi):
    """QQ 机器人绑定、自有机器人与渠道配置相关接口。"""

    def get_bind_link(
        self, refresh: bool = False, bot_app_id: Optional[str] = None
    ) -> QqBotBindLink:
        """获取绑定链接与绑定码；``refresh=True`` 时旧绑定码失效并重新生成。

        ``bot_app_id`` 为空时为分配给当前用户的官方机器人。
        """

        path = self.append_query(
            "/api/open/qqBot/getBindLink",
            {"refresh": "true" if refresh else None, "botAppId": bot_app_id or None},
        )
        return self.execute_open("GET", path, None, QqBotBindLink)

    def bot_info(self, bot_app_id: Optional[str] = None) -> QqBotBindInfo:
        """查询绑定状态；``bot_app_id`` 为空时为默认机器人。"""

        return self.execute_open(
            "GET", self._with_bot_app_id("/api/open/qqBot/botInfo", bot_app_id), None, QqBotBindInfo
        )

    def unbind(self, bot_app_id: Optional[str] = None) -> None:
        """解绑 QQ 机器人；``bot_app_id`` 为空时解绑官方机器人。"""

        self.execute_open(
            "GET", self._with_bot_app_id("/api/open/qqBot/unbind", bot_app_id), None, None
        )

    def group_list(self, bot_app_id: Optional[str] = None) -> List[QqGroupItem]:
        """获取机器人已加入的 QQ 群列表；``bot_app_id`` 为空时返回全部。"""

        result = self.execute_open(
            "GET",
            self._with_bot_app_id("/api/open/qqBot/groupList", bot_app_id),
            None,
            List[QqGroupItem],
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
        """新增渠道配置：发到指定 QQ 群（sendType=2），或用指定机器人发给自己（sendType=1）。"""

        self.execute_open(
            "POST", "/api/open/qqBot/add", _with_default_send_type(request), None
        )

    def edit(self, request: QqBotSaveRequest) -> None:
        """修改渠道配置；配置编码不可修改，但需传原值。"""

        self.execute_open(
            "POST", "/api/open/qqBot/edit", _with_default_send_type(request), None
        )

    def delete(self, config_id: int) -> None:
        """删除渠道配置。"""

        path = self.append_query("/api/open/qqBot/delete", {"id": int(config_id)})
        self.execute_open("DELETE", path, None, None)

    def my_bots(self) -> QqMyBotList:
        """我的 QQ 机器人列表：官方与自有机器人及其绑定状态、自有机器人接入信息。"""

        return self.execute_open("GET", "/api/open/qqBot/myBots", None, QqMyBotList)

    def preview_custom_bot(self, request: QqCustomBotRequest) -> QqBotInfo:
        """校验自有机器人凭证并获取头像昵称，不会保存。"""

        return self.execute_open(
            "POST", "/api/open/qqBot/customBot/preview", request, QqBotInfo
        )

    def add_custom_bot(self, request: QqCustomBotRequest) -> None:
        """添加自有机器人。"""

        self.execute_open("POST", "/api/open/qqBot/customBot/add", request, None)

    def edit_custom_bot(self, request: QqCustomBotRequest) -> None:
        """修改自有机器人的 AppSecret。"""

        self.execute_open("POST", "/api/open/qqBot/customBot/edit", request, None)

    def refresh_custom_bot(self, bot_app_id: str) -> None:
        """刷新自有机器人的头像昵称。"""

        path = self.append_query("/api/open/qqBot/customBot/refresh", {"botAppId": bot_app_id})
        self.execute_open("GET", path, None, None)

    def delete_custom_bot(self, bot_app_id: str) -> None:
        """删除自有机器人，同时删除该机器人上的绑定、QQ 群与渠道配置。"""

        path = self.append_query("/api/open/qqBot/customBot/delete", {"botAppId": bot_app_id})
        self.execute_open("DELETE", path, None, None)

    def set_default(self, bot_app_id: str) -> None:
        """设置默认 QQ 机器人，需已绑定；发送时不填 ``option`` 即用默认机器人发给自己。"""

        path = self.append_query("/api/open/qqBot/setDefault", {"botAppId": bot_app_id})
        self.execute_open("GET", path, None, None)

    def _with_bot_app_id(self, path: str, bot_app_id: Optional[str]) -> str:
        return self.append_query(path, {"botAppId": bot_app_id or None})


def _with_default_send_type(request: QqBotSaveRequest) -> QqBotSaveRequest:
    if request is None or request.sendType is not None:
        return request
    return replace(request, sendType=SEND_TYPE_QQ_GROUP)


__all__ = ["QqBotApi", "SEND_TYPE_SELF", "SEND_TYPE_QQ_GROUP"]
