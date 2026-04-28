"""AccessKey 管理器：缓存 + 过期前自动刷新 + 多线程安全。"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from .config import PushPlusConfig
from .exceptions import PushPlusError

if TYPE_CHECKING:
    from .api.access_key import AccessKeyApi


_logger = logging.getLogger("perk_pushplus")


class AccessKeyManager:
    """提供线程安全的 AccessKey 缓存与过期前自动刷新能力。

    在调用任意需要 ``access-key`` 的开放接口前，:class:`OpenApi` 基类会
    自动通过本类拿到一个有效的 AccessKey。

    刷新策略：在 ``expiresIn`` 到期前 :attr:`PushPlusConfig.access_key_refresh_ahead_seconds`
    秒视为过期。文档说明老 key 在新 key 生成后 5 分钟内仍可用，因此默认 300 秒提前量足够安全。

    线程安全：多线程并发调用 :meth:`get_access_key` 时仅会触发一次刷新。
    """

    def __init__(self, config: PushPlusConfig, access_key_api: "AccessKeyApi") -> None:
        self._config = config
        self._api = access_key_api
        self._lock = threading.Lock()
        self._cached_key: Optional[str] = None
        self._expire_at: datetime = datetime.min

    def get_access_key(self) -> str:
        """获取有效的 AccessKey。如已缓存且未过期则直接返回；否则触发刷新。"""

        if self._is_valid():
            return self._cached_key  # type: ignore[return-value]
        return self.refresh()

    def refresh(self) -> str:
        """强制刷新。多线程并发调用时仅会真正发起一次刷新请求。"""

        with self._lock:
            if self._is_valid():
                return self._cached_key  # type: ignore[return-value]
            result = self._api.get_access_key()
            if result is None or not result.accessKey:
                raise PushPlusError("获取 AccessKey 失败：返回为空")
            ttl_seconds = int(result.expiresIn) if result.expiresIn is not None else 7200
            ahead = max(0, int(self._config.access_key_refresh_ahead_seconds))
            effective_ttl = max(1, ttl_seconds - ahead)
            self._cached_key = result.accessKey
            self._expire_at = datetime.now() + timedelta(seconds=effective_ttl)
            _logger.debug(
                "[pushplus] AccessKey refreshed, ttl=%ss, refresh in <= %ss",
                ttl_seconds,
                effective_ttl,
            )
            return self._cached_key

    def invalidate(self) -> None:
        """失效缓存。下次调用 :meth:`get_access_key` 时会重新拉取。"""

        with self._lock:
            self._cached_key = None
            self._expire_at = datetime.min

    def _is_valid(self) -> bool:
        return self._cached_key is not None and datetime.now() < self._expire_at


__all__ = ["AccessKeyManager"]
