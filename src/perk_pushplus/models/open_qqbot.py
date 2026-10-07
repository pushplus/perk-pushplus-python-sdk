"""开放接口 - QQ 机器人模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QqBotBindLink:
    """QQ 机器人绑定链接与绑定码。"""

    url: Optional[str] = None
    """带参分享链接，用于生成扫码二维码；已绑定用户再次获取时可能为空。"""
    bindCode: Optional[str] = None
    """绑定码。已是好友时扫码收不到加好友事件，需私聊发送该码；认领 QQ 群也用此码。"""
    expireSeconds: Optional[int] = None
    """有效期秒数，默认 300。"""
    botAppId: Optional[str] = None
    """要绑定的机器人 appId；未指定 ``bot_app_id`` 时为分配给当前用户的官方机器人。"""
    botName: Optional[str] = None
    botAvatar: Optional[str] = None
    botType: Optional[int] = None
    """1-官方机器人，2-自有机器人。"""


@dataclass
class QqBotInfo:
    """QQ 机器人详情。"""

    botId: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    botAppId: Optional[str] = None
    shareUrl: Optional[str] = None
    """官方分享链接，可用于拉机器人进群。"""
    botType: Optional[int] = None
    """1-官方机器人，2-自有机器人。"""


@dataclass
class QqMyBot:
    """用户可用的 QQ 机器人及其绑定状态。"""

    botAppId: Optional[str] = None
    botId: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    shareUrl: Optional[str] = None
    """官方分享链接，可用于拉机器人进群。"""
    botType: Optional[int] = None
    """1-官方机器人，2-自有机器人。"""
    isBind: Optional[int] = None
    """0-未绑定，1-已绑定。"""
    receiveStatus: Optional[int] = None
    """1-可接收，0-用户已关闭单聊接收。"""
    isDefault: Optional[int] = None
    """1-默认机器人；发送时不填 ``option`` 即用默认机器人发给自己。"""
    bindTime: Optional[str] = None


@dataclass
class QqMyBotList:
    """我的 QQ 机器人列表，附带自有机器人的接入信息。"""

    bots: Optional[List[QqMyBot]] = None
    """官方机器人在前，自有机器人在后。"""
    customBotCount: Optional[int] = None
    """已添加的自有机器人数。"""
    customBotLimit: Optional[int] = None
    """可添加的自有机器人上限。"""
    webhookUrl: Optional[str] = None
    """需在 QQ 开放平台配置的回调地址。"""
    serverIps: Optional[List[str]] = None
    """需加入 QQ 开放平台 IP 白名单的服务器出口 IP。"""
    events: Optional[List[str]] = None
    """需在 QQ 开放平台订阅的事件。"""


@dataclass
class QqCustomBotRequest:
    """校验/添加/修改自有 QQ 机器人请求。"""

    botAppId: Optional[str] = None
    """QQ 开放平台 AppID，必填，最多 32 个字符。"""
    appSecret: Optional[str] = None
    """QQ 开放平台 AppSecret，必填，最多 64 个字符。"""


@dataclass
class QqBotBindInfo:
    """QQ 机器人绑定状态。"""

    isBind: Optional[int] = None
    """0-未绑定，1-已绑定。"""
    receiveStatus: Optional[int] = None
    """1-可接收，0-用户已关闭单聊接收。"""
    createTime: Optional[str] = None
    botInfo: Optional[QqBotInfo] = None


@dataclass
class QqGroupItem:
    """机器人已加入的 QQ 群。"""

    id: Optional[int] = None
    """群编号；新增渠道配置时作为 ``qqGroupId`` 使用。"""
    groupOpenId: Optional[str] = None
    groupRemark: Optional[str] = None
    status: Optional[int] = None
    """1-在群，2-群消息接收关闭。"""
    groupName: Optional[str] = None
    """群名称，接口未授权时为空。"""
    groupFingerMemo: Optional[str] = None
    groupClassText: Optional[str] = None
    groupTags: Optional[List[str]] = None
    groupMemberNum: Optional[int] = None
    createTime: Optional[str] = None


@dataclass
class QqBotItem:
    """QQ 机器人渠道配置列表项。"""

    id: Optional[int] = None
    qqName: Optional[str] = None
    qqCode: Optional[str] = None
    """配置编码；发送消息时作为 ``option`` 传入。"""
    sendType: Optional[int] = None
    """1-发给自己，2-发到 QQ 群。"""
    qqGroupId: Optional[int] = None
    """``sendType=2`` 时返回。"""
    groupRemark: Optional[str] = None
    groupOpenId: Optional[str] = None
    groupName: Optional[str] = None
    botAppId: Optional[str] = None
    """发送使用的机器人 appId。"""
    botName: Optional[str] = None
    botAvatar: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class QqBotSaveRequest:
    """新增/修改 QQ 机器人渠道配置请求。"""

    id: Optional[int] = None
    """修改时必填。"""
    qqName: Optional[str] = None
    """配置名称，必填，最多 64 个字符。"""
    qqCode: Optional[str] = None
    """配置编码，必填（修改时传原值）；仅支持字母、数字、下划线和中划线，创建后不可修改。"""
    sendType: Optional[int] = None
    """发送类型：1-发给自己，2-发到 QQ 群；留空时 SDK 自动填 2。"""
    qqGroupId: Optional[int] = None
    """QQ 群编号，``sendType=2`` 时必填，取自 ``group_list`` 返回的 ``id``。"""
    botAppId: Optional[str] = None
    """发送使用的机器人 appId；``sendType=1`` 时必填，``sendType=2`` 时可不填，以群所在机器人为准。"""


__all__ = [
    "QqBotBindLink",
    "QqBotInfo",
    "QqBotBindInfo",
    "QqGroupItem",
    "QqBotItem",
    "QqBotSaveRequest",
    "QqMyBot",
    "QqMyBotList",
    "QqCustomBotRequest",
]
