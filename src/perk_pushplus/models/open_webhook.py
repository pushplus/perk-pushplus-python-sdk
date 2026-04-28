"""开放接口 - webhook 渠道配置模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..enums import WebhookType


@dataclass
class WebhookItem:
    """webhook 列表项。"""

    id: Optional[int] = None
    webhookCode: Optional[str] = None
    webhookName: Optional[str] = None
    webhookType: Optional[int] = None
    webhookTypeName: Optional[str] = None
    webhookUrl: Optional[str] = None
    createTime: Optional[str] = None
    httpMethod: Optional[str] = None
    headers: Optional[str] = None
    body: Optional[str] = None

    def get_webhook_type_enum(self) -> Optional[WebhookType]:
        return WebhookType.of(self.webhookType)


@dataclass
class WebhookSaveRequest:
    """新增/修改 webhook 请求体（id 仅修改时使用）。"""

    id: Optional[int] = None
    webhookCode: Optional[str] = None
    webhookName: Optional[str] = None
    webhookType: Optional[int] = None
    webhookUrl: Optional[str] = None
    httpMethod: Optional[str] = None
    headers: Optional[str] = None
    body: Optional[str] = None


__all__ = ["WebhookItem", "WebhookSaveRequest"]
