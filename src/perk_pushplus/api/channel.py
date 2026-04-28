"""开放接口 - 微信公众号/企业微信/邮箱渠道列表（文档「七. 渠道配置接口」 5-8）。"""
from __future__ import annotations

from typing import Optional

from ..models import CpItem, MailDetail, MailItem, MpItem, PageQuery, PageResult
from .base import OpenAbstractApi


class ChannelApi(OpenAbstractApi):
    """微信公众号 / 企业微信 / 邮箱渠道列表。"""

    def mp_list(self, query: Optional[PageQuery] = None) -> PageResult[MpItem]:
        """微信公众号渠道列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/mp/list", body, PageResult[MpItem]
        )
        return result or PageResult(list=[])

    def cp_list(self, query: Optional[PageQuery] = None) -> PageResult[CpItem]:
        """企业微信应用渠道列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/cp/list", body, PageResult[CpItem]
        )
        return result or PageResult(list=[])

    def mail_list(self, query: Optional[PageQuery] = None) -> PageResult[MailItem]:
        """邮箱渠道列表。"""

        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/mail/list", body, PageResult[MailItem]
        )
        return result or PageResult(list=[])

    def mail_detail(self, mail_id: int) -> MailDetail:
        """邮箱渠道详情。"""

        path = self.append_query("/api/open/mail/detail", {"mailId": int(mail_id)})
        return self.execute_open("GET", path, None, MailDetail)


__all__ = ["ChannelApi"]
