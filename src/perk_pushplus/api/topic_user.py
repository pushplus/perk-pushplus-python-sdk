"""开放接口 - 群组用户接口（文档「六. 群组用户接口」）。"""
from __future__ import annotations

from ..models import PageResult, TopicUserItem, TopicUserListQuery
from .base import OpenAbstractApi


class TopicUserApi(OpenAbstractApi):
    """群组内用户管理。"""

    def subscriber_list(self, query: TopicUserListQuery) -> PageResult[TopicUserItem]:
        """获取群组内用户。"""

        result = self.execute_open(
            "POST", "/api/open/topicUser/subscriberList", query, PageResult[TopicUserItem]
        )
        return result or PageResult(list=[])

    def delete_user(self, topic_relation_id: int) -> str:
        """删除群组内用户。"""

        path = self.append_query(
            "/api/open/topicUser/deleteTopicUser",
            {"topicRelationId": int(topic_relation_id)},
        )
        return self.execute_open("POST", path, None, str)

    def edit_remark(self, id_: int, remark: str) -> None:
        """修改订阅人备注。"""

        body = {"id": int(id_), "remark": remark}
        self.execute_open("POST", "/api/open/topicUser/editRemark", body, None)


__all__ = ["TopicUserApi"]
