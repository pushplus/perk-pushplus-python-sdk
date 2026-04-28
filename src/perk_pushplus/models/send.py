"""发送消息相关请求/响应模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..enums import Channel, Template


@dataclass
class SendRequest:
    """发送消息请求（``/send``）。

    推荐使用 :meth:`builder` 链式构建。``token`` 不填时由 SDK 自动注入。
    """

    token: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    topic: Optional[str] = None
    template: Optional[Template] = None
    channel: Optional[Channel] = None
    option: Optional[str] = None
    callbackUrl: Optional[str] = None
    timestamp: Optional[int] = None
    to: Optional[str] = None
    pre: Optional[str] = None

    @staticmethod
    def builder() -> "SendRequestBuilder":
        return SendRequestBuilder()


class SendRequestBuilder:
    """:class:`SendRequest` 的链式 Builder，用法对齐 Java 版。"""

    def __init__(self) -> None:
        self._req = SendRequest()

    def token(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.token = value
        return self

    def title(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.title = value
        return self

    def content(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.content = value
        return self

    def topic(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.topic = value
        return self

    def template(self, value: Optional[Template]) -> "SendRequestBuilder":
        self._req.template = value
        return self

    def channel(self, value: Optional[Channel]) -> "SendRequestBuilder":
        self._req.channel = value
        return self

    def option(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.option = value
        return self

    def callback_url(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.callbackUrl = value
        return self

    def timestamp(self, value: Optional[int]) -> "SendRequestBuilder":
        self._req.timestamp = value
        return self

    def to(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.to = value
        return self

    def pre(self, value: Optional[str]) -> "SendRequestBuilder":
        self._req.pre = value
        return self

    def build(self) -> SendRequest:
        return SendRequest(
            token=self._req.token,
            title=self._req.title,
            content=self._req.content,
            topic=self._req.topic,
            template=self._req.template,
            channel=self._req.channel,
            option=self._req.option,
            callbackUrl=self._req.callbackUrl,
            timestamp=self._req.timestamp,
            to=self._req.to,
            pre=self._req.pre,
        )


@dataclass
class BatchSendRequest:
    """多渠道发送消息请求（``/batchSend``）。

    ``channel`` / ``option`` 为多个渠道用逗号拼接的字符串，与官方文档保持一致；
    使用 :meth:`builder` 累加风格构建会自动拼接。
    """

    token: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    topic: Optional[str] = None
    template: Optional[Template] = None
    channel: Optional[str] = None
    option: Optional[str] = None
    callbackUrl: Optional[str] = None
    timestamp: Optional[int] = None
    to: Optional[str] = None
    pre: Optional[str] = None

    @staticmethod
    def builder() -> "BatchSendRequestBuilder":
        return BatchSendRequestBuilder()


class BatchSendRequestBuilder:
    """:class:`BatchSendRequest` 链式 Builder。

    支持累加风格（与 Java 一致）::

        BatchSendRequest.builder() \
            .title("多渠道告警") \
            .content("CPU > 90%") \
            .channel(Channel.WECHAT).option("") \
            .channel(Channel.WEBHOOK).option("bark") \
            .channel(Channel.EXTENSION).option("") \
            .build()
    """

    def __init__(self) -> None:
        self.token_value: Optional[str] = None
        self.title_value: Optional[str] = None
        self.content_value: Optional[str] = None
        self.topic_value: Optional[str] = None
        self.template_value: Optional[Template] = None
        self.callback_url_value: Optional[str] = None
        self.timestamp_value: Optional[int] = None
        self.to_value: Optional[str] = None
        self.pre_value: Optional[str] = None

        self._channel_csv: Optional[str] = None
        self._option_csv: Optional[str] = None
        self._channel_list: List[Channel] = []
        self._option_list: List[str] = []

    def token(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.token_value = value
        return self

    def title(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.title_value = value
        return self

    def content(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.content_value = value
        return self

    def topic(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.topic_value = value
        return self

    def template(self, value: Optional[Template]) -> "BatchSendRequestBuilder":
        self.template_value = value
        return self

    def callback_url(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.callback_url_value = value
        return self

    def timestamp(self, value: Optional[int]) -> "BatchSendRequestBuilder":
        self.timestamp_value = value
        return self

    def to(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.to_value = value
        return self

    def pre(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        self.pre_value = value
        return self

    def channel(self, value: Channel) -> "BatchSendRequestBuilder":
        """追加一个 channel；与最近一次 :meth:`option` 配对。"""

        self._channel_list.append(value)
        return self

    def option(self, value: Optional[str]) -> "BatchSendRequestBuilder":
        """追加一个 option，可传空串。"""

        self._option_list.append("" if value is None else value)
        return self

    def channel_string(self, csv: Optional[str]) -> "BatchSendRequestBuilder":
        """直接以 CSV 形式指定多渠道字符串。"""

        self._channel_csv = csv
        return self

    def option_string(self, csv: Optional[str]) -> "BatchSendRequestBuilder":
        """直接以 CSV 形式指定 option 字符串。"""

        self._option_csv = csv
        return self

    def build(self) -> BatchSendRequest:
        if self._channel_list:
            final_channel = ",".join(ch.value for ch in self._channel_list)
        else:
            final_channel = self._channel_csv
        if self._option_list:
            final_option = ",".join(self._option_list)
        else:
            final_option = self._option_csv
        return BatchSendRequest(
            token=self.token_value,
            title=self.title_value,
            content=self.content_value,
            topic=self.topic_value,
            template=self.template_value,
            channel=final_channel,
            option=final_option,
            callbackUrl=self.callback_url_value,
            timestamp=self.timestamp_value,
            to=self.to_value,
            pre=self.pre_value,
        )


@dataclass
class BatchSendResult:
    """批量发送的单条渠道结果。"""

    shortCode: Optional[str] = None
    message: Optional[str] = None
    code: Optional[int] = None
    channel: Optional[Channel] = None


__all__ = [
    "SendRequest",
    "SendRequestBuilder",
    "BatchSendRequest",
    "BatchSendRequestBuilder",
    "BatchSendResult",
]
