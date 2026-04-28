"""开放接口 - 群组 / 群组用户模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional, Union


Number = Union[int, float, Decimal, str]


@dataclass
class TopicItem:
    """群组列表项。"""

    icon: Optional[str] = None
    topicId: Optional[int] = None
    topicCode: Optional[str] = None
    topicName: Optional[str] = None
    nickName: Optional[str] = None
    createTime: Optional[str] = None
    topicUserCount: Optional[int] = None
    topicType: Optional[int] = None
    """0 普通；1 积分；2 公开。"""
    isApproved: Optional[int] = None
    firstIsApproved: Optional[int] = None
    approveReason: Optional[str] = None
    isOpen: Optional[int] = None


@dataclass
class TopicDetail:
    """群组详情（我创建的 / 我加入的复用此类，未返回字段为 ``None``）。"""

    topicId: Optional[int] = None
    topicName: Optional[str] = None
    topicCode: Optional[str] = None
    qrCodeImgUrl: Optional[str] = None
    contact: Optional[str] = None
    introduction: Optional[str] = None
    receiptMessage: Optional[str] = None
    nickName: Optional[str] = None
    createTime: Optional[str] = None
    topicUserCount: Optional[int] = None
    icon: Optional[str] = None
    appId: Optional[str] = None
    topicType: Optional[int] = None
    price: Optional[Number] = None
    topicDescribe: Optional[str] = None
    userNickName: Optional[str] = None
    isApproved: Optional[int] = None
    firstIsApproved: Optional[int] = None
    approveReason: Optional[str] = None
    isOpen: Optional[int] = None


@dataclass
class TopicQrCode:
    """群组二维码。"""

    qrCodeImgUrl: Optional[str] = None
    forever: Optional[int] = None
    """0-临时二维码，1-永久二维码。"""


@dataclass
class TopicListQuery:
    """群组列表查询。

    官方接口结构是 ``{current, pageSize, params:{topicType}}``。
    """

    current: Optional[int] = None
    pageSize: Optional[int] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def of(
        cls,
        current: Optional[int] = 1,
        page_size: Optional[int] = 20,
        topic_type: Optional[int] = 0,
    ) -> "TopicListQuery":
        params: Dict[str, Any] = {}
        if topic_type is not None:
            params["topicType"] = topic_type
        return cls(current=current, pageSize=page_size, params=params or None)


@dataclass
class TopicUserListQuery:
    """获取群组内用户分页查询。"""

    current: Optional[int] = None
    pageSize: Optional[int] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def of(
        cls,
        current: Optional[int],
        page_size: Optional[int],
        topic_id: int,
    ) -> "TopicUserListQuery":
        return cls(current=current, pageSize=page_size, params={"topicId": topic_id})


@dataclass
class TopicUserItem:
    """群组内用户。"""

    id: Optional[int] = None
    nickName: Optional[str] = None
    openId: Optional[str] = None
    headImgUrl: Optional[str] = None
    userSex: Optional[int] = None
    havePhone: Optional[int] = None
    isFollow: Optional[int] = None
    emailStatus: Optional[int] = None
    followTime: Optional[str] = None
    remark: Optional[str] = None


@dataclass
class TopicAddRequest:
    """新增群组请求。"""

    topicCode: Optional[str] = None
    topicName: Optional[str] = None
    contact: Optional[str] = None
    introduction: Optional[str] = None
    receiptMessage: Optional[str] = None
    appId: Optional[str] = None
    icon: Optional[str] = None
    topicType: Optional[int] = None
    """0 普通；1 积分；2 公开。默认 0。"""
    price: Optional[Number] = None
    topicDescribe: Optional[str] = None


@dataclass
class TopicEditRequest:
    """修改群组请求。"""

    topic: Optional[int] = None
    """群组编号，必填。"""
    topicCode: Optional[str] = None
    topicName: Optional[str] = None
    contact: Optional[str] = None
    introduction: Optional[str] = None
    receiptMessage: Optional[str] = None
    icon: Optional[str] = None
    price: Optional[Number] = None
    topicDescribe: Optional[str] = None


__all__ = [
    "TopicItem",
    "TopicDetail",
    "TopicQrCode",
    "TopicListQuery",
    "TopicUserListQuery",
    "TopicUserItem",
    "TopicAddRequest",
    "TopicEditRequest",
]
