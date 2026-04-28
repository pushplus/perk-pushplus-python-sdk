"""PushPlus SDK 统一入口。"""
from __future__ import annotations

from concurrent.futures import Future
from typing import List, Optional

from .access_key import AccessKeyManager
from .api import (
    AccessKeyApi,
    ChannelApi,
    ClawBotApi,
    FriendApi,
    MessageApi,
    MessageTokenApi,
    OpenMessageApi,
    PreApi,
    SettingApi,
    TopicApi,
    TopicUserApi,
    UserApi,
    WebhookApi,
)
from .config import PushPlusConfig
from .exceptions import PushPlusError
from .http import HttpRequester, RequestsHttpRequester
from .models import BatchSendRequest, BatchSendResult, SendRequest
from .rate_limit import RateLimitGuard


class PushPlusClient:
    """PushPlus SDK 客户端。

    线程安全，建议作为单例长期持有。

    快速使用::

        from perk_pushplus import PushPlusClient

        client = PushPlusClient.builder() \
            .token("your_user_token") \
            .secret_key("your_secret_key") \
            .build()

        # 发送消息
        short_code = client.send_simple("标题", "内容")

        # 调用开放接口（无需手动管理 AccessKey）
        info = client.user.my_info()
    """

    def __init__(
        self,
        config: PushPlusConfig,
        http_requester: Optional[HttpRequester] = None,
    ) -> None:
        if config is None:
            raise PushPlusError("PushPlusConfig 不能为空")
        self.config = config
        self.http_requester: HttpRequester = http_requester or RequestsHttpRequester(config)
        self.rate_limit_guard = RateLimitGuard(config)

        self.message = MessageApi(config, self.http_requester, self.rate_limit_guard)
        self.access_key_api = AccessKeyApi(config, self.http_requester)
        self.access_key_manager = AccessKeyManager(config, self.access_key_api)

        self.open_message = OpenMessageApi(config, self.http_requester, self.access_key_manager)
        self.user = UserApi(config, self.http_requester, self.access_key_manager)
        self.message_token = MessageTokenApi(config, self.http_requester, self.access_key_manager)
        self.topic = TopicApi(config, self.http_requester, self.access_key_manager)
        self.topic_user = TopicUserApi(config, self.http_requester, self.access_key_manager)
        self.friend = FriendApi(config, self.http_requester, self.access_key_manager)
        self.webhook = WebhookApi(config, self.http_requester, self.access_key_manager)
        self.channel = ChannelApi(config, self.http_requester, self.access_key_manager)
        self.claw_bot = ClawBotApi(config, self.http_requester, self.access_key_manager)
        self.setting = SettingApi(config, self.http_requester, self.access_key_manager)
        self.pre = PreApi(config, self.http_requester, self.access_key_manager)

    @classmethod
    def of(cls, config: PushPlusConfig) -> "PushPlusClient":
        return cls(config)

    @classmethod
    def builder(cls) -> "PushPlusClientBuilder":
        return PushPlusClientBuilder()

    def send_simple(self, title: Optional[str], content: str) -> str:
        """发送一条简单消息（默认 wechat / html）。"""

        return self.message.send_simple(title, content)

    def send(self, request: SendRequest) -> str:
        return self.message.send(request)

    def send_async(self, request: SendRequest) -> "Future[str]":
        return self.message.send_async(request)

    def batch_send(self, request: BatchSendRequest) -> List[BatchSendResult]:
        return self.message.batch_send(request)

    def batch_send_async(self, request: BatchSendRequest) -> "Future[List[BatchSendResult]]":
        return self.message.batch_send_async(request)


class PushPlusClientBuilder:
    """:class:`PushPlusClient` 链式 Builder。"""

    def __init__(self) -> None:
        self._config = PushPlusConfig()
        self._http_requester: Optional[HttpRequester] = None
        self._full_config: Optional[PushPlusConfig] = None

    def token(self, value: Optional[str]) -> "PushPlusClientBuilder":
        self._config.token = value
        return self

    def secret_key(self, value: Optional[str]) -> "PushPlusClientBuilder":
        self._config.secret_key = value
        return self

    def base_url(self, value: str) -> "PushPlusClientBuilder":
        self._config.base_url = value
        return self

    def connect_timeout(self, seconds: float) -> "PushPlusClientBuilder":
        self._config.connect_timeout = float(seconds)
        return self

    def read_timeout(self, seconds: float) -> "PushPlusClientBuilder":
        self._config.read_timeout = float(seconds)
        return self

    def access_key_refresh_ahead_seconds(self, seconds: int) -> "PushPlusClientBuilder":
        self._config.access_key_refresh_ahead_seconds = int(seconds)
        return self

    def log_request(self, enabled: bool) -> "PushPlusClientBuilder":
        self._config.log_request = bool(enabled)
        return self

    def rate_limit_guard_enabled(self, enabled: bool) -> "PushPlusClientBuilder":
        self._config.rate_limit_guard_enabled = bool(enabled)
        return self

    def rate_limit_cooldown_seconds(self, seconds: Optional[float]) -> "PushPlusClientBuilder":
        self._config.rate_limit_cooldown_seconds = (
            None if seconds is None else float(seconds)
        )
        return self

    def user_agent(self, value: str) -> "PushPlusClientBuilder":
        self._config.user_agent = value
        return self

    def http_requester(self, requester: HttpRequester) -> "PushPlusClientBuilder":
        self._http_requester = requester
        return self

    def config(self, config: PushPlusConfig) -> "PushPlusClientBuilder":
        """直接传入完整 config，覆盖之前的 setter。"""

        self._full_config = config
        return self

    def build(self) -> PushPlusClient:
        cfg = self._full_config if self._full_config is not None else self._config
        return PushPlusClient(cfg, self._http_requester)


__all__ = ["PushPlusClient", "PushPlusClientBuilder"]
