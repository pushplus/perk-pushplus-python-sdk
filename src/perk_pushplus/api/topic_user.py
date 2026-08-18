"""开放接口 - 群组用户接口（文档「六. 群组用户接口」）。"""
from __future__ import annotations

from ..models import PageResult, TopicUserBlacklistItem, TopicUserItem, TopicUserListQuery
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

    def add_blacklist(self, topic_relation_id: int) -> None:
        """将订阅人加入黑名单。

        加入后将移出群组，对方无法再加入该群组。积分群组不支持黑名单。不能将自己加入黑名单。
        """

        path = self.append_query(
            "/api/open/topicUser/addBlacklist",
            {"topicRelationId": int(topic_relation_id)},
        )
        self.execute_open("POST", path, None, None)

    def blacklist_list(
        self, query: TopicUserListQuery
    ) -> PageResult[TopicUserBlacklistItem]:
        """订阅人黑名单列表。``query.params.topicId`` 必填。"""

        result = self.execute_open(
            "POST",
            "/api/open/topicUser/blacklistList",
            query,
            PageResult[TopicUserBlacklistItem],
        )
        return result or PageResult(list=[])

    def remove_blacklist(self, id_: int) -> None:
        """解除订阅人黑名单。

        解除后不会自动恢复群组订阅，对方可重新加入该群组。
        """

        path = self.append_query("/api/open/topicUser/removeBlacklist", {"id": int(id_)})
        self.execute_open("POST", path, None, None)


__all__ = ["TopicUserApi"]
