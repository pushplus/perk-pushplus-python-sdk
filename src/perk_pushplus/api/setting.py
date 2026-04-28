"""开放接口 - 功能设置（文档「九. 功能设置接口」）。"""
from __future__ import annotations

from typing import Optional

from ..models import (
    PageQuery,
    PageResult,
    UserDefaultDetail,
    UserDefaultItem,
    UserDefaultSaveRequest,
)
from .base import OpenAbstractApi


class SettingApi(OpenAbstractApi):
    """功能设置 / 默认配置 / 各类开关。"""

    def list_user_default(
        self, query: Optional[PageQuery] = None
    ) -> PageResult[UserDefaultItem]:
        """获取默认配置列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/setting/listUserDefault", body, PageResult[UserDefaultItem]
        )
        return result or PageResult(list=[])

    def detail_user_default(self, id_: int) -> UserDefaultDetail:
        """默认配置详情。"""

        path = self.append_query(
            "/api/open/setting/detailUserDefault", {"id": int(id_)}
        )
        return self.execute_open("GET", path, None, UserDefaultDetail)

    def add_user_default(self, req: UserDefaultSaveRequest) -> None:
        """新增默认配置。"""

        self.execute_open("POST", "/api/open/setting/addUserDefault", req, None)

    def edit_user_default(self, req: UserDefaultSaveRequest) -> None:
        """修改默认配置。"""

        self.execute_open("POST", "/api/open/setting/editUserDefault", req, None)

    def delete_user_default(self, id_: int) -> None:
        """删除默认配置。"""

        path = self.append_query(
            "/api/open/setting/deleteUserDefault", {"id": int(id_)}
        )
        self.execute_open("DELETE", path, None, None)

    def change_receive_limit(self, recevie_limit: int) -> None:
        """修改接收消息限制：0 接收全部，1 不接收消息。"""

        path = self.append_query(
            "/api/open/setting/changeRecevieLimit", {"recevieLimit": int(recevie_limit)}
        )
        self.execute_open("GET", path, None, None)

    def change_is_send(self, is_send: int) -> None:
        """开启/关闭发送消息功能：0 禁用，1 启用。"""

        path = self.append_query(
            "/api/open/setting/changeIsSend", {"isSend": int(is_send)}
        )
        self.execute_open("GET", path, None, None)

    def change_open_message_type(self, open_message_type: int) -> None:
        """修改打开消息方式：0 H5，1 小程序。"""

        path = self.append_query(
            "/api/open/setting/changeOpenMessageType",
            {"openMessageType": int(open_message_type)},
        )
        self.execute_open("GET", path, None, None)

    def change_extension_forward(self, forward: int) -> None:
        """修改插件渠道转发：0 否，1 是。"""

        path = self.append_query(
            "/api/open/setting/extension", {"forward": int(forward)}
        )
        self.execute_open("GET", path, None, None)


__all__ = ["SettingApi"]
