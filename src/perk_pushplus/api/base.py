"""API 基类：提供请求执行、统一错误处理、access-key 自动注入与重试。"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Type, TypeVar
from urllib.parse import quote

from ..config import PushPlusConfig
from ..exceptions import PushPlusError
from ..http import HttpRequester, to_json
from ..models.base import ApiResponse, model_from_dict, model_to_dict

if TYPE_CHECKING:
    from ..access_key import AccessKeyManager


T = TypeVar("T")
HEADER_ACCESS_KEY = "access-key"
_CODE_ACCESS_KEY_INVALID = 401


class AbstractApi:
    """API 基类。"""

    def __init__(self, config: PushPlusConfig, http: HttpRequester) -> None:
        self.config = config
        self.http = http

    def resolve_url(self, path: str) -> str:
        """拼接绝对 URL。"""

        if path.startswith("http://") or path.startswith("https://"):
            return path
        base = self.config.resolve_base_url()
        return base + (path if path.startswith("/") else "/" + path)

    @staticmethod
    def build_query(params: Optional[Mapping[str, Any]]) -> str:
        """把 mapping 拼成 query string；忽略 ``None`` 值。"""

        if not params:
            return ""
        parts = []
        for key, value in params.items():
            if value is None:
                continue
            parts.append(f"{quote(str(key), safe='')}={quote(str(value), safe='')}")
        return "&".join(parts)

    @classmethod
    def append_query(cls, path: str, params: Optional[Mapping[str, Any]]) -> str:
        """在 path 上追加 query string。"""

        q = cls.build_query(params)
        if not q:
            return path
        sep = "&" if "?" in path else "?"
        return f"{path}{sep}{q}"

    def execute(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]],
        body: Any,
        data_type: Optional[Type[T]] = None,
    ) -> ApiResponse[T]:
        """执行请求并返回原始 :class:`ApiResponse`（不进行 code 校验）。"""

        url = self.resolve_url(path)
        body_json: Optional[str]
        if body is None:
            body_json = None
        elif isinstance(body, str):
            body_json = body
        else:
            body_json = to_json(model_to_dict(body))
        resp = self.http.execute(method, url, headers, body_json)
        if not resp.is_successful:
            raise PushPlusError(
                f"PushPlus 接口 HTTP 调用失败: status={resp.status_code}, body={resp.body}",
                code=resp.status_code,
            )
        return self._parse_api_response(resp.body, data_type)

    def execute_for_data(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]],
        body: Any,
        data_type: Optional[Type[T]] = None,
    ) -> Optional[T]:
        """执行请求并直接返回 ``data``；非 200 抛出异常。"""

        resp = self.execute(method, path, headers, body, data_type)
        if not resp.is_success():
            raise PushPlusError(
                self._build_business_error_message("PushPlus 接口业务失败", resp),
                code=resp.code if resp.code is not None else -1,
            )
        return resp.data

    @staticmethod
    def _parse_api_response(
        response_body: str, data_type: Optional[Type[T]] = None
    ) -> ApiResponse[T]:
        if response_body is None or response_body == "":
            raise PushPlusError("PushPlus 接口返回为空")
        try:
            payload = json.loads(response_body)
        except (TypeError, ValueError) as exc:
            raise PushPlusError(
                f"解析 PushPlus 响应 JSON 失败: {exc}, payload={response_body}", cause=exc
            ) from exc
        if not isinstance(payload, dict):
            raise PushPlusError(f"PushPlus 接口返回非 JSON 对象: {response_body}")

        result: ApiResponse[T] = ApiResponse(
            code=payload.get("code"), msg=payload.get("msg"), data=None
        )
        data_node = payload.get("data")
        if result.is_success():
            if data_node is None:
                result.data = None
                return result
            try:
                if data_type is None:
                    result.data = data_node
                else:
                    result.data = model_from_dict(data_type, data_node)
            except Exception as exc:  # noqa: BLE001
                raise PushPlusError(
                    f"解析 PushPlus 响应 data 字段失败: {exc}, payload={response_body}",
                    cause=exc,
                ) from exc
            return result
        # 业务失败：把 data 中的字符串/简单值附加到 msg。
        data_text = AbstractApi._extract_data_text(data_node)
        if data_text:
            if not result.msg:
                result.msg = data_text
            elif data_text not in result.msg:
                result.msg = f"{result.msg}: {data_text}"
        return result

    @staticmethod
    def _extract_data_text(data_node: Any) -> Optional[str]:
        if data_node is None:
            return None
        if isinstance(data_node, (str, int, float, bool)):
            return str(data_node)
        try:
            return json.dumps(data_node, ensure_ascii=False)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _build_business_error_message(prefix: str, resp: ApiResponse) -> str:
        return f"{prefix}: code={resp.code}, msg={resp.msg}"


class OpenAbstractApi(AbstractApi):
    """开放接口基类。

    会自动在 header 中带上 ``access-key``，并在收到 ``code=401`` 时尝试刷新 AccessKey 后重试一次。
    """

    def __init__(
        self,
        config: PushPlusConfig,
        http: HttpRequester,
        access_key_manager: "AccessKeyManager",
    ) -> None:
        super().__init__(config, http)
        self.access_key_manager = access_key_manager

    def _headers_with_access_key(self) -> Dict[str, str]:
        return {HEADER_ACCESS_KEY: self.access_key_manager.get_access_key()}

    def execute_open(
        self,
        method: str,
        path: str,
        body: Any = None,
        data_type: Optional[Type[T]] = None,
    ) -> Optional[T]:
        """执行带 ``access-key`` 的请求；当返回 ``code=401`` 时自动刷新 key 并重试一次。"""

        headers = self._headers_with_access_key()
        resp = self.execute(method, path, headers, body, data_type)
        if resp.is_success():
            return resp.data
        if resp.code is not None and int(resp.code) == _CODE_ACCESS_KEY_INVALID:
            self.access_key_manager.invalidate()
            retry_headers = self._headers_with_access_key()
            retry = self.execute(method, path, retry_headers, body, data_type)
            if retry.is_success():
                return retry.data
            raise PushPlusError(
                f"PushPlus 开放接口业务失败(重试后): code={retry.code}, msg={retry.msg}",
                code=retry.code if retry.code is not None else -1,
            )
        raise PushPlusError(
            f"PushPlus 开放接口业务失败: code={resp.code}, msg={resp.msg}",
            code=resp.code if resp.code is not None else -1,
        )


__all__ = ["AbstractApi", "OpenAbstractApi", "HEADER_ACCESS_KEY"]
