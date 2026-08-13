"""开放接口 - push 表格（文档：https://www.pushplus.plus/doc/ecosystem/sheet/）。"""
from __future__ import annotations

import json
from typing import Any, Optional, Sequence

from ..models import DocListItem, DocListQuery, ExcelContent, ExcelVo, PageResult
from .base import OpenAbstractApi


class ExcelApi(OpenAbstractApi):
    """push 表格管理。"""

    def list(self, query: Optional[DocListQuery] = None) -> PageResult[DocListItem]:
        body = query if query is not None else DocListQuery()
        result = self.execute_open(
            "POST", "/push/api/open/excel/list", body, PageResult[DocListItem]
        )
        return result or PageResult(list=[])

    def create(self, title: str) -> ExcelVo:
        """创建空白表格。"""

        return self.execute_open(
            "POST", "/push/api/open/excel/create", {"title": title}, ExcelVo
        )

    def content(self, doc_code: str) -> ExcelContent:
        """获取表格元信息与整表 JSON 草稿。"""

        path = self.append_query("/push/api/open/excel/content", {"docCode": doc_code})
        return self.execute_open("GET", path, None, ExcelContent)

    def save_content(self, doc_code: str, content: Any) -> ExcelVo:
        """整表覆盖保存草稿。

        ``content`` 可为 JSON 字符串，或工作簿 ``dict``（SDK 会序列化）。
        """

        return self.execute_open(
            "POST",
            "/push/api/open/excel/saveContent",
            {"docCode": doc_code, "content": _as_json_string(content)},
            ExcelVo,
        )

    def write_cells(
        self,
        doc_code: str,
        range_: str,
        values: Sequence[Sequence[Any]],
        sheet_name: Optional[str] = None,
    ) -> ExcelVo:
        """从指定起始单元格起，按二维数组向右向下写入（草稿）。"""

        body: dict = {"docCode": doc_code, "range": range_, "values": list(values)}
        if sheet_name is not None:
            body["sheetName"] = sheet_name
        return self.execute_open("POST", "/push/api/open/excel/writeCells", body, ExcelVo)

    def publish(self, doc_code: str) -> ExcelVo:
        """将草稿同步为分享页快照。"""

        path = self.append_query("/push/api/open/excel/publish", {"docCode": doc_code})
        return self.execute_open("POST", path, None, ExcelVo)

    def rename(self, doc_code: str, title: str) -> None:
        self.execute_open(
            "POST",
            "/push/api/open/excel/rename",
            {"docCode": doc_code, "title": title},
            None,
        )

    def delete(self, doc_code: str) -> None:
        path = self.append_query("/push/api/open/excel/delete", {"docCode": doc_code})
        self.execute_open("POST", path, None, None)

    def update_share(
        self, doc_code: str, share_perm: int, share_login: Optional[int] = None
    ) -> ExcelVo:
        """更新分享设置：``share_perm`` 0 关闭 / 1 开启；``share_login`` 0 免登录 / 1 需登录。"""

        body = {"docCode": doc_code, "sharePerm": int(share_perm)}
        if share_login is not None:
            body["shareLogin"] = int(share_login)
        return self.execute_open("POST", "/push/api/open/excel/updateShare", body, ExcelVo)


def _as_json_string(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)


__all__ = ["ExcelApi"]
