"""开放接口 - 获取 AccessKey。"""
from __future__ import annotations

from typing import Optional

from ..config import PushPlusConfig
from ..exceptions import PushPlusError
from ..http import HttpRequester
from ..models import AccessKeyResult
from .base import AbstractApi


class AccessKeyApi(AbstractApi):
    """对应文档「一. 获取 AccessKey」。"""

    def __init__(self, config: PushPlusConfig, http: HttpRequester) -> None:
        super().__init__(config, http)

    def get_access_key(
        self,
        token: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> AccessKeyResult:
        """获取 AccessKey。

        ``token`` / ``secret_key`` 不传时使用 :class:`PushPlusConfig` 中的配置。
        """

        token = token or self.config.token
        secret_key = secret_key or self.config.secret_key
        if not token:
            raise PushPlusError("获取 AccessKey 需要 token")
        if not secret_key:
            raise PushPlusError("获取 AccessKey 需要 secretKey")
        body = {"token": token, "secretKey": secret_key}
        result = self.execute_for_data(
            "POST", "/api/common/openApi/getAccessKey", None, body, AccessKeyResult
        )
        if result is None:
            raise PushPlusError("获取 AccessKey 失败：返回为空")
        return result


__all__ = ["AccessKeyApi"]
