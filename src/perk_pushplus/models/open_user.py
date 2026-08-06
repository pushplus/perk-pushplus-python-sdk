"""开放接口 - 用户接口模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VipInfo:
    """会员信息。"""

    isVip: Optional[int] = None
    """是否会员；0-否，1-是。"""
    lastDay: Optional[str] = None
    """会员到期日。"""


@dataclass
class UserInfo:
    """个人资料详情。"""

    openId: Optional[str] = None
    unionId: Optional[str] = None
    nickName: Optional[str] = None
    headImgUrl: Optional[str] = None
    userSex: Optional[int] = None
    token: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    emailStatus: Optional[int] = None
    birthday: Optional[str] = None
    points: Optional[int] = None
    vipInfo: Optional[VipInfo] = None
    """会员信息。"""
    verifyStatus: Optional[int] = None
    """实名认证状态；0-未实名，1-已实名。"""


@dataclass
class UserLimitTime:
    """解封剩余时间。"""

    sendLimit: Optional[int] = None
    """1-无限制，2-短期限制，3-永久限制。"""
    userLimitTime: Optional[str] = None


@dataclass
class SendCount:
    """当日消息接口请求次数。"""

    wechatSendCount: Optional[int] = None
    cpSendCount: Optional[int] = None
    webhookSendCount: Optional[int] = None
    mailSendCount: Optional[int] = None


__all__ = ["VipInfo", "UserInfo", "UserLimitTime", "SendCount"]
