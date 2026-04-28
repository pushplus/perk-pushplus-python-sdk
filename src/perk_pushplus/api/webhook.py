"""开放接口 - webhook 渠道配置（文档「七. 渠道配置接口」 1-4）。"""
from __future__ import annotations

from typing import Optional

from ..models import PageQuery, PageResult, WebhookItem, WebhookSaveRequest
from .base import OpenAbstractApi


class WebhookApi(OpenAbstractApi):
    """webhook 渠道管理。"""

    def list(self, query: Optional[PageQuery] = None) -> PageResult[WebhookItem]:
        body = query if query is not None else PageQuery()
        result = self.execute_open(
            "POST", "/api/open/webhook/list", body, PageResult[WebhookItem]
        )
        return result or PageResult(list=[])

    def detail(self, webhook_id: int) -> WebhookItem:
        path = self.append_query(
            "/api/open/webhook/detail", {"webhookId": int(webhook_id)}
        )
        return self.execute_open("GET", path, None, WebhookItem)

    def add(self, req: WebhookSaveRequest) -> int:
        """新增 webhook，返回新 id。"""

        return self.execute_open("POST", "/api/open/webhook/add", req, int)

    def edit(self, req: WebhookSaveRequest) -> str:
        return self.execute_open("POST", "/api/open/webhook/edit", req, str)


__all__ = ["WebhookApi"]
