"""HTTP 请求执行层。

默认提供基于 ``requests`` 的实现，调用方也可以传入自定义 :class:`HttpRequester`，
方便在 Lambda、aiohttp、httpx 等环境中替换底层实现。
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, runtime_checkable

import requests

from .config import PushPlusConfig
from .exceptions import PushPlusError


_logger = logging.getLogger("perk_pushplus")


@dataclass
class HttpResponse:
    """简化的 HTTP 响应对象。"""

    status_code: int
    body: str

    @property
    def is_successful(self) -> bool:
        return 200 <= self.status_code < 300


@runtime_checkable
class HttpRequester(Protocol):
    """HTTP 请求执行接口。"""

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[str],
    ) -> HttpResponse: ...


class RequestsHttpRequester:
    """基于 ``requests`` 的 :class:`HttpRequester` 默认实现，线程安全可复用。"""

    def __init__(self, config: PushPlusConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._connect_timeout = float(config.connect_timeout)
        self._read_timeout = float(config.read_timeout)
        self._log_request = bool(config.log_request)

    @property
    def session(self) -> requests.Session:
        return self._session

    def close(self) -> None:
        try:
            self._session.close()
        except Exception:  # noqa: BLE001
            pass

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[str],
    ) -> HttpResponse:
        merged_headers: Dict[str, str] = {}
        if self._config.user_agent:
            merged_headers["User-Agent"] = self._config.user_agent
        if self._config.extra_headers:
            merged_headers.update(self._config.extra_headers)
        if headers:
            for k, v in headers.items():
                if k is None or v is None:
                    continue
                merged_headers[k] = v

        has_content_type = any(k.lower() == "content-type" for k in merged_headers)
        if body is not None and not has_content_type:
            merged_headers["Content-Type"] = "application/json;charset=UTF-8"

        if self._log_request:
            _logger.debug("[pushplus] >>> %s %s body=%s", method, url, body)

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                data=body.encode("utf-8") if body is not None else None,
                headers=merged_headers,
                timeout=(self._connect_timeout, self._read_timeout),
                allow_redirects=True,
            )
        except requests.RequestException as exc:
            raise PushPlusError(
                f"调用 PushPlus 接口失败(IO异常): {exc}", code=-1, cause=exc
            ) from exc

        text = response.text or ""
        if self._log_request:
            _logger.debug("[pushplus] <<< status=%s body=%s", response.status_code, text)
        return HttpResponse(status_code=response.status_code, body=text)


def to_json(payload: Any) -> str:
    """把任意对象序列化为 JSON 字符串，自动跳过 ``None`` 字段。

    用于发送请求 body：与 Java 端 ``JsonInclude.NON_NULL`` 行为对齐。
    """
    if payload is None:
        return "null"
    if isinstance(payload, str):
        return payload
    return json.dumps(_strip_none(payload), ensure_ascii=False, default=_default)


def _strip_none(value: Any) -> Any:
    """递归剔除 ``None`` 字段。"""

    if isinstance(value, dict):
        return {k: _strip_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [_strip_none(v) for v in value if v is not None]
    return value


def _default(obj: Any) -> Any:
    """通用 JSON 序列化兜底。"""

    # 枚举：统一取 .value（与 Java 的 @JsonValue 行为一致）。
    if hasattr(obj, "value") and obj.__class__.__module__ != "builtins":
        try:
            return obj.value
        except Exception:  # noqa: BLE001
            pass
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict()
        except Exception:  # noqa: BLE001
            pass
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


__all__ = [
    "HttpRequester",
    "RequestsHttpRequester",
    "HttpResponse",
    "to_json",
]
