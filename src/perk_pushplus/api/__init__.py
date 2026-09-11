"""API 子包入口。"""
from .access_key import AccessKeyApi
from .base import AbstractApi, OpenAbstractApi
from .channel import ChannelApi
from .clawbot import ClawBotApi
from .friend import FriendApi
from .image import ImageApi
from .form import FormApi
from .doc import DocApi
from .excel import ExcelApi
from .forward_log import ForwardLogApi
from .forward_rule import ForwardRuleApi
from .message import MessageApi
from .message_token import MessageTokenApi
from .open_message import OpenMessageApi
from .pre import PreApi
from .qqbot import QqBotApi
from .setting import SettingApi
from .topic import TopicApi
from .topic_user import TopicUserApi
from .user import UserApi
from .webhook import WebhookApi

__all__ = [
    "AbstractApi",
    "OpenAbstractApi",
    "AccessKeyApi",
    "MessageApi",
    "OpenMessageApi",
    "UserApi",
    "MessageTokenApi",
    "TopicApi",
    "TopicUserApi",
    "FriendApi",
    "WebhookApi",
    "ChannelApi",
    "ClawBotApi",
    "QqBotApi",
    "SettingApi",
    "PreApi",
    "ImageApi",
    "FormApi",
    "DocApi",
    "ExcelApi",
    "ForwardRuleApi",
    "ForwardLogApi",
]
