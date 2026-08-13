"""开放接口 - push 文档（文档：https://www.pushplus.plus/doc/ecosystem/doc/）。"""
from __future__ import annotations

from typing import Optional

from ..models import DocContent, DocListItem, DocListQuery, DocVo, PageResult
from .base import OpenAbstractApi


class DocApi(OpenAbstractApi):
    """push 文档管理。"""

    def list(self, query: Optional[DocListQuery] = None) -> PageResult[DocListItem]:
        body = query if query is not None else DocListQuery()
        result = self.execute_open(
            "POST", "/push/api/open/doc/list", body, PageResult[DocListItem]
        )
        return result or PageResult(list=[])

    def create(self, title: str) -> DocVo:
        """创建空白文档。"""

        return self.execute_open("POST", "/push/api/open/doc/create", {"title": title}, DocVo)

    def content(self, doc_code: str) -> DocContent:
        """获取文档元信息与 HTML 草稿正文。"""

        path = self.append_query("/push/api/open/doc/content", {"docCode": doc_code})
        return self.execute_open("GET", path, None, DocContent)

    def save_content(self, doc_code: str, content: str) -> DocVo:
        """保存 HTML 草稿（不影响分享页，需再 publish）。"""

        return self.execute_open(
            "POST",
            "/push/api/open/doc/saveContent",
            {"docCode": doc_code, "content": content},
            DocVo,
        )

    def publish(self, doc_code: str) -> DocVo:
        """将草稿同步为分享页快照。"""

        path = self.append_query("/push/api/open/doc/publish", {"docCode": doc_code})
        return self.execute_open("POST", path, None, DocVo)

    def rename(self, doc_code: str, title: str) -> None:
        self.execute_open(
            "POST",
            "/push/api/open/doc/rename",
            {"docCode": doc_code, "title": title},
            None,
        )

    def delete(self, doc_code: str) -> None:
        path = self.append_query("/push/api/open/doc/delete", {"docCode": doc_code})
        self.execute_open("POST", path, None, None)

    def update_share(
        self, doc_code: str, share_perm: int, share_login: Optional[int] = None
    ) -> DocVo:
        """更新分享设置：``share_perm`` 0 关闭 / 1 开启；``share_login`` 0 免登录 / 1 需登录。"""

        body = {"docCode": doc_code, "sharePerm": int(share_perm)}
        if share_login is not None:
            body["shareLogin"] = int(share_login)
        return self.execute_open("POST", "/push/api/open/doc/updateShare", body, DocVo)


__all__ = ["DocApi"]
