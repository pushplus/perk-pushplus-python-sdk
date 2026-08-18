"""开放接口 - 好友功能（文档「十. 好友功能接口」）。"""
from __future__ import annotations

from typing import Optional

from ..models import FriendBlacklistItem, FriendItem, FriendQrCode, PageQuery, PageResult
from .base import OpenAbstractApi


class FriendApi(OpenAbstractApi):
    """好友相关接口。"""

    def get_qr_code(
        self,
        app_id: Optional[str] = None,
        content: Optional[str] = None,
        second: Optional[int] = None,
        scan_count: Optional[int] = None,
    ) -> FriendQrCode:
        """获取个人二维码。"""

        params = {}
        if app_id is not None:
            params["appId"] = app_id
        if content is not None:
            params["content"] = content
        if second is not None:
            params["second"] = int(second)
        if scan_count is not None:
            params["scanCount"] = int(scan_count)
        path = self.append_query("/api/open/friend/getQrCode", params)
        return self.execute_open("GET", path, None, FriendQrCode)

    def list(self, query: Optional[PageQuery] = None) -> PageResult[FriendItem]:
        """获取好友列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/friend/list", body, PageResult[FriendItem]
        )
        return result or PageResult(list=[])

    def delete(self, friend_id: int) -> None:
        """删除好友。"""

        path = self.append_query(
            "/api/open/friend/deleteFriend", {"friendId": int(friend_id)}
        )
        self.execute_open("GET", path, None, None)

    def edit_remark(self, id_: int, remark: str) -> None:
        """修改好友备注。"""

        body = {"id": int(id_), "remark": remark}
        self.execute_open("POST", "/api/open/friend/editRemark", body, None)

    def add_blacklist(self, friend_id: int) -> None:
        """将好友加入黑名单。

        加入后将解除双方好友关系，对方无法再添加你。不能将自己加入黑名单，仅可将已有好友加入黑名单。
        """

        path = self.append_query(
            "/api/open/friend/addBlacklist", {"friendId": int(friend_id)}
        )
        self.execute_open("POST", path, None, None)

    def blacklist_list(
        self, query: Optional[PageQuery] = None
    ) -> PageResult[FriendBlacklistItem]:
        """好友黑名单列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/friend/blacklistList", body, PageResult[FriendBlacklistItem]
        )
        return result or PageResult(list=[])

    def remove_blacklist(self, id_: int) -> None:
        """解除好友黑名单。

        解除后不会自动恢复好友关系，需重新扫码添加。
        """

        path = self.append_query("/api/open/friend/removeBlacklist", {"id": int(id_)})
        self.execute_open("POST", path, None, None)


__all__ = ["FriendApi"]
