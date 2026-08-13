"""开放接口 - push 表单（文档：https://www.pushplus.plus/doc/ecosystem/form/）。"""
from __future__ import annotations

from typing import Optional

from ..models import (
    FormDetail,
    FormListItem,
    FormListQuery,
    FormPublishDiff,
    FormPublishResult,
    FormSaveRequest,
    PageResult,
)
from .base import OpenAbstractApi


class FormApi(OpenAbstractApi):
    """push 表单管理。"""

    def list(self, query: Optional[FormListQuery] = None) -> PageResult[FormListItem]:
        body = query if query is not None else FormListQuery()
        result = self.execute_open(
            "POST", "/push/api/open/form/list", body, PageResult[FormListItem]
        )
        return result or PageResult(list=[])

    def create(self, title: str) -> FormListItem:
        """创建空白表单（草稿）。"""

        return self.execute_open(
            "POST", "/push/api/open/form/create", {"title": title}, FormListItem
        )

    def copy(self, form_id: int) -> FormListItem:
        """基于已有表单复制一份新草稿。"""

        path = self.append_query("/push/api/open/form/copy", {"id": int(form_id)})
        return self.execute_open("POST", path, None, FormListItem)

    def save(self, req: FormSaveRequest) -> None:
        """保存表单设计（仅更新草稿；已发布需再调用 publish）。"""

        self.execute_open("POST", "/push/api/open/form/save", req, None)

    def detail(self, form_id: int) -> FormDetail:
        path = self.append_query("/push/api/open/form/detail", {"id": int(form_id)})
        return self.execute_open("GET", path, None, FormDetail)

    def publish_diff(self, form_id: int) -> FormPublishDiff:
        """草稿与发布快照的题目差异。"""

        path = self.append_query("/push/api/open/form/publishDiff", {"id": int(form_id)})
        return self.execute_open("GET", path, None, FormPublishDiff)

    def publish(self, form_id: int) -> FormPublishResult:
        """发布表单，开始收集。"""

        path = self.append_query("/push/api/open/form/publish", {"id": int(form_id)})
        return self.execute_open("POST", path, None, FormPublishResult)

    def stop(self, form_id: int) -> None:
        """停止收集。"""

        path = self.append_query("/push/api/open/form/stop", {"id": int(form_id)})
        self.execute_open("POST", path, None, None)

    def delete(self, form_id: int) -> None:
        """删除表单（不可恢复）。"""

        path = self.append_query("/push/api/open/form/delete", {"id": int(form_id)})
        self.execute_open("POST", path, None, None)


__all__ = ["FormApi"]
