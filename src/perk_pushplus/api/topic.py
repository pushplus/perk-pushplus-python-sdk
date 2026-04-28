"""开放接口 - 群组接口（文档「五. 群组接口」）。"""
from __future__ import annotations

from typing import Optional

from ..models import (
    PageResult,
    TopicAddRequest,
    TopicDetail,
    TopicEditRequest,
    TopicItem,
    TopicListQuery,
    TopicQrCode,
)
from .base import OpenAbstractApi


class TopicApi(OpenAbstractApi):
    """群组管理。"""

    def list(self, query: Optional[TopicListQuery] = None) -> PageResult[TopicItem]:
        body = query if query is not None else TopicListQuery()
        result = self.execute_open(
            "POST", "/api/open/topic/list", body, PageResult[TopicItem]
        )
        return result or PageResult(list=[])

    def detail(self, topic_id: int) -> TopicDetail:
        """获取我创建的群组详情。"""

        path = self.append_query("/api/open/topic/detail", {"topicId": int(topic_id)})
        return self.execute_open("GET", path, None, TopicDetail)

    def join_detail(self, topic_id: int) -> TopicDetail:
        """获取我加入的群详情。"""

        path = self.append_query(
            "/api/open/topic/joinTopicDetail", {"topicId": int(topic_id)}
        )
        return self.execute_open("GET", path, None, TopicDetail)

    def add(self, req: TopicAddRequest) -> int:
        """新增群组，返回新建群组编号。"""

        return self.execute_open("POST", "/api/open/topic/add", req, int)

    def edit(self, req: TopicEditRequest) -> str:
        """修改群组。"""

        return self.execute_open("POST", "/api/open/topic/editTopic", req, str)

    def qr_code(
        self,
        topic_id: int,
        second: Optional[int] = None,
        scan_count: Optional[int] = None,
    ) -> TopicQrCode:
        """获取群组二维码。"""

        params = {"topicId": int(topic_id)}
        if second is not None:
            params["second"] = int(second)
        if scan_count is not None:
            params["scanCount"] = int(scan_count)
        path = self.append_query("/api/open/topic/qrCode", params)
        return self.execute_open("GET", path, None, TopicQrCode)

    def exit(self, topic_id: int) -> str:
        """退出群组。"""

        path = self.append_query(
            "/api/open/topic/exitTopic", {"topicId": int(topic_id)}
        )
        return self.execute_open("GET", path, None, str)

    def delete(self, topic_id: int) -> str:
        """删除群组。"""

        path = self.append_query("/api/open/topic/delete", {"topicId": int(topic_id)})
        return self.execute_open("GET", path, None, str)

    def set_open(self, topic_id: int, is_open: int) -> str:
        """上下架积分群组：``is_open`` 1 上架；0 下架。"""

        body = {"topic": int(topic_id), "isOpen": int(is_open)}
        return self.execute_open("POST", "/api/open/topic/isOpen", body, str)


__all__ = ["TopicApi"]
