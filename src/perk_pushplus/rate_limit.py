"""本地限流守卫：命中 ``code=900`` 后短路同 token 后续发送请求。"""
from __future__ import annotations

import logging
import threading
from datetime import date, datetime, time, timedelta
from typing import Callable, Dict, Optional

from .config import PushPlusConfig
from .enums import ErrorCode
from .exceptions import PushPlusError


_logger = logging.getLogger("perk_pushplus")


class RateLimitGuard:
    """本地限流守卫。

    当 PushPlus 服务端返回 :class:`ErrorCode.RATE_LIMITED`（``code=900``）时，
    在内存里按 ``token`` 维度记录 "解禁时间"，期间任何发送类调用都会直接抛
    :class:`PushPlusError`（``code=900``），避免继续打到上游浪费请求并加重账号限制。

    对应官方文档建议：https://www.pushplus.plus/doc/guide/code.html

    禁推时长：默认到"次日 0 点"自动解禁；也可以通过 :attr:`PushPlusConfig.rate_limit_cooldown_seconds`
    配置一个固定时长（设置后优先生效）。

    线程安全；多线程并发安全使用。**仅本地视角**：服务端实际禁推时长可能与本地估算不同
    （文档示例为 2 天）。本守卫只是把客户端视为"今日已被限流"以避免无效请求，
    解禁后若服务端仍在限流，会再次返回 900 并重新触发本地短路。
    """

    def __init__(
        self,
        config: PushPlusConfig,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._config = config
        self._clock = clock or datetime.now
        self._lock = threading.Lock()
        self._blocked_until: Dict[str, datetime] = {}

    def check(self, token: Optional[str]) -> None:
        """在发起发送类请求前调用：若当前 token 处于限流期，直接抛 :class:`PushPlusError`。

        开关关闭（:attr:`PushPlusConfig.rate_limit_guard_enabled` = ``False``）时直接放行。
        """
        if not self._config.rate_limit_guard_enabled:
            return
        key = self._normalize(token)
        if key is None:
            return
        with self._lock:
            until = self._blocked_until.get(key)
            now = self._clock()
            if until is None:
                return
            if now < until:
                raise PushPlusError(
                    "PushPlus 本地限流守卫：当前 token 已命中 code=900，"
                    f"在 {until.isoformat()} 之前不再发起请求（请参考官方文档减少无用请求）",
                    code=ErrorCode.RATE_LIMITED.code,
                )
            # 已经到期，清除登记。
            self._blocked_until.pop(key, None)

    def mark_blocked(self, token: Optional[str]) -> None:
        """在收到服务端 ``code=900`` 后调用：登记限流状态。"""
        if not self._config.rate_limit_guard_enabled:
            return
        key = self._normalize(token)
        if key is None:
            return
        now = self._clock()
        until = self._cooldown_until(now)
        with self._lock:
            self._blocked_until[key] = until
        _logger.warning(
            "[pushplus] 命中 code=900，本地限流守卫将拒绝该 token 的发送请求至 %s（token 末位: %s）",
            until.isoformat(),
            self._tail(key),
        )

    def clear(self, token: Optional[str]) -> None:
        """手动清除指定 token 的本地限流状态。"""
        key = self._normalize(token)
        if key is None:
            return
        with self._lock:
            self._blocked_until.pop(key, None)

    def blocked_until(self, token: Optional[str]) -> Optional[datetime]:
        """返回该 token 的解禁时间；未被限流则为 ``None``。"""
        key = self._normalize(token)
        if key is None:
            return None
        with self._lock:
            return self._blocked_until.get(key)

    def _cooldown_until(self, now: datetime) -> datetime:
        cooldown = self._config.rate_limit_cooldown_seconds
        if cooldown is not None and cooldown > 0:
            return now + timedelta(seconds=float(cooldown))
        # 默认：次日 0 点。
        tomorrow = (now.date() if isinstance(now, datetime) else date.today()) + timedelta(days=1)
        return datetime.combine(tomorrow, time.min)

    @staticmethod
    def _normalize(token: Optional[str]) -> Optional[str]:
        if token is None:
            return None
        s = token.strip()
        return s or None

    @staticmethod
    def _tail(token: str) -> str:
        if len(token) <= 4:
            return "****"
        return "****" + token[-4:]


__all__ = ["RateLimitGuard"]
