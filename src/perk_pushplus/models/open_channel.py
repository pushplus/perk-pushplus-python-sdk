"""开放接口 - 微信公众号 / 企业微信 / 邮箱渠道模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MpItem:
    """微信公众号渠道列表项。"""

    id: Optional[int] = None
    nickName: Optional[str] = None
    headImg: Optional[str] = None
    principalName: Optional[str] = None
    authorizationAppid: Optional[str] = None
    funcInfo: Optional[str] = None
    serviceType: Optional[int] = None
    verifyType: Optional[int] = None
    alias: Optional[str] = None
    updateTime: Optional[str] = None


@dataclass
class CpItem:
    """企业微信应用渠道列表项。"""

    id: Optional[int] = None
    cpName: Optional[str] = None
    cpCode: Optional[str] = None


@dataclass
class MailItem:
    """邮箱渠道列表项。"""

    id: Optional[int] = None
    mailName: Optional[str] = None
    mailCode: Optional[str] = None


@dataclass
class MailDetail:
    """邮箱渠道详情。"""

    id: Optional[int] = None
    mailName: Optional[str] = None
    mailCode: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    smtpServer: Optional[str] = None
    smtpSsl: Optional[int] = None
    smtpPort: Optional[int] = None
    createTime: Optional[str] = None


__all__ = ["MpItem", "CpItem", "MailItem", "MailDetail"]
