"""发送消息接口（``/send`` 与 ``/batchSend``）。"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import List, Optional

from ..config import PushPlusConfig
from ..exceptions import PushPlusError
from ..http import HttpRequester
from ..models import BatchSendRequest, BatchSendResult, SendRequest
from ..rate_limit import RateLimitGuard
from .base import AbstractApi


class MessageApi(AbstractApi):
    """对应 PushPlus 文档「二. 发送消息接口」与「三. 多渠道发送消息接口」。

    内置本地限流守卫：当上游返回 ``code=900`` 时，后续对同 token 的发送调用会
    在 SDK 内被直接短路抛 :class:`PushPlusError`。可以通过
    :attr:`PushPlusConfig.rate_limit_guard_enabled` 关闭。
    """

    def __init__(
        self,
        config: PushPlusConfig,
        http: HttpRequester,
        rate_limit_guard: Optional[RateLimitGuard] = None,
    ) -> None:
        super().__init__(config, http)
        self.rate_limit_guard = rate_limit_guard or RateLimitGuard(config)
        self._executor: Optional[ThreadPoolExecutor] = None

    def get_rate_limit_guard(self) -> RateLimitGuard:
        return self.rate_limit_guard

    def send(self, request: SendRequest) -> str:
        """发送单条消息（同步），返回消息流水号 ``shortCode``。

        ``request.token`` 为空时会自动注入 :attr:`PushPlusConfig.token`。
        """

        req = self._with_default_token(request)
        self._validate_send(req)
        self.rate_limit_guard.check(req.token)
        return self._execute_with_guard(
            req.token,
            lambda: self.execute_for_data("POST", "/send", None, req, str),
        )

    def send_async(self, request: SendRequest) -> "Future[str]":
        """发送单条消息（异步）；返回 :class:`concurrent.futures.Future`。"""

        return self._executor_instance().submit(self.send, request)

    def batch_send(self, request: BatchSendRequest) -> List[BatchSendResult]:
        """多渠道发送消息，返回每个渠道一个 :class:`BatchSendResult`。"""

        req = self._with_default_token_batch(request)
        self._validate_batch(req)
        self.rate_limit_guard.check(req.token)
        result = self._execute_with_guard(
            req.token,
            lambda: self.execute_for_data(
                "POST", "/batchSend", None, req, List[BatchSendResult]
            ),
        )
        return result or []

    def batch_send_async(self, request: BatchSendRequest) -> "Future[List[BatchSendResult]]":
        """多渠道发送消息（异步）。"""

        return self._executor_instance().submit(self.batch_send, request)

    def send_simple(self, title: Optional[str], content: str) -> str:
        """便捷方法：以默认渠道（wechat）、默认模板（html）发送一条消息。"""

        return self.send(SendRequest.builder().title(title).content(content).build())

    def _execute_with_guard(self, token: Optional[str], call):
        try:
            return call()
        except PushPlusError as exc:
            if exc.is_rate_limited():
                self.rate_limit_guard.mark_blocked(token)
            raise

    def _executor_instance(self) -> ThreadPoolExecutor:
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=4, thread_name_prefix="pushplus-send"
            )
        return self._executor

    def _with_default_token(self, request: SendRequest) -> SendRequest:
        if request is None:
            raise PushPlusError("SendRequest 不能为空")
        if request.token and request.token.strip():
            return request
        token = self._require_token()
        return SendRequest(
            token=token,
            title=request.title,
            content=request.content,
            topic=request.topic,
            template=request.template,
            channel=request.channel,
            option=request.option,
            callbackUrl=request.callbackUrl,
            timestamp=request.timestamp,
            to=request.to,
            pre=request.pre,
        )

    def _with_default_token_batch(self, request: BatchSendRequest) -> BatchSendRequest:
        if request is None:
            raise PushPlusError("BatchSendRequest 不能为空")
        if request.token and request.token.strip():
            return request
        token = self._require_token()
        return BatchSendRequest(
            token=token,
            title=request.title,
            content=request.content,
            topic=request.topic,
            template=request.template,
            channel=request.channel,
            option=request.option,
            callbackUrl=request.callbackUrl,
            timestamp=request.timestamp,
            to=request.to,
            pre=request.pre,
        )

    def _require_token(self) -> str:
        token = self.config.token
        if not token or not token.strip():
            raise PushPlusError("发送消息需要 token，但 PushPlusConfig.token 为空")
        return token

    @staticmethod
    def _validate_send(req: SendRequest) -> None:
        if not req.content or not req.content.strip():
            raise PushPlusError("发送消息 content 不能为空")

    @staticmethod
    def _validate_batch(req: BatchSendRequest) -> None:
        if not req.content or not req.content.strip():
            raise PushPlusError("批量发送消息 content 不能为空")


__all__ = ["MessageApi"]
