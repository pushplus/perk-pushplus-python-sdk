"""PushPlus SDK 全局配置。"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional


DEFAULT_BASE_URL = "https://www.pushplus.plus"
"""PushPlus 默认服务地址。"""


@dataclass
class PushPlusConfig:
    """PushPlus SDK 全局配置。

    所有字段都有合理的默认值，仅 ``token`` 是发送消息接口必填、
    ``secret_key`` 是开放接口必填。
    """

    token: Optional[str] = None
    """用户 token 或消息 token，发送消息接口默认使用。

    注意：获取 AccessKey 必须使用用户 token。
    """

    secret_key: Optional[str] = None
    """用户 secretKey，调用开放接口（获取 AccessKey）必填。

    在 PushPlus 个人中心 -> 开发设置 中配置。
    """

    base_url: str = DEFAULT_BASE_URL
    """服务器基础地址。默认 ``https://www.pushplus.plus``。"""

    connect_timeout: float = 10.0
    """连接超时（秒）。默认 10 秒。"""

    read_timeout: float = 30.0
    """请求/读超时（秒）。默认 30 秒。"""

    access_key_refresh_ahead_seconds: int = 300
    """在 AccessKey 过期前提前多少秒刷新。默认提前 5 分钟（300 秒）。

    PushPlus 文档说明老 AccessKey 在新 AccessKey 生成后 5 分钟内仍可用，因此提前 5 分钟刷新最稳妥。
    """

    log_request: bool = False
    """是否启用请求/响应详细日志（DEBUG 级别）。默认关闭。"""

    rate_limit_guard_enabled: bool = True
    """是否启用本地限流守卫。默认开启。

    开启后，当任意一次发送消息接口返回 ``code=900``（请求次数过多）时，
    后续对同一 token 的发送调用会被 SDK 直接短路，不再发起 HTTP，
    直到 :attr:`rate_limit_cooldown_seconds`（默认次日 0 点）到期。
    """

    rate_limit_cooldown_seconds: Optional[float] = None
    """命中 ``code=900`` 后的本地禁推时长（秒）。``None`` 表示使用默认策略：到"次日 0 点"。

    服务端实际禁推时长可能更长（文档示例为 2 天）。如已知账号被长期封禁，
    可显式设置 ``2 * 86400`` 等更长值来减少无用试探。
    """

    user_agent: str = "perk-pushplus-python-sdk/1.0.1"
    """HTTP User-Agent 头。"""

    extra_headers: dict = field(default_factory=dict)
    """自定义附加请求头，会与每次请求头合并。"""

    def resolve_base_url(self) -> str:
        """返回有效的 base_url，去除尾部 ``/``。"""

        url = self.base_url
        if not url:
            return DEFAULT_BASE_URL
        return url.rstrip("/")

    def with_overrides(self, **kwargs) -> "PushPlusConfig":
        """返回一个覆盖了部分字段的新配置（不修改原对象）。"""

        return replace(self, **kwargs)


__all__ = ["PushPlusConfig", "DEFAULT_BASE_URL"]
