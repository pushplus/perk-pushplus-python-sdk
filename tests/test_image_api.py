"""图片服务接口测试（文档「十二. 图片服务接口」）。"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple, Union

import pytest

from perk_pushplus import (
    HttpResponse,
    ImageItem,
    ImageUploadResult,
    ImageUploadToken,
    PageQuery,
    PushPlusClient,
    PushPlusError,
)


class ImageScriptedRequester:
    """支持 execute / execute_raw 双通道的 mock。

    PushPlus 开放接口（取凭证 / 列表 / 删除）走 ``execute``，
    七牛云 multipart 上传走 ``execute_raw``，可分别注册响应。
    """

    def __init__(self) -> None:
        self.calls: List[
            Tuple[str, str, str, Optional[Dict[str, str]], Optional[Union[str, bytes]]]
        ] = []
        # (channel, url_suffix, status, body)
        self.responses: List[Tuple[str, str, int, str]] = []
        self.access_keys: List[str] = ["ak-1"]

    def push(self, url_suffix: str, status: int, body: str) -> None:
        self.responses.append(("execute", url_suffix, status, body))

    def push_raw(self, url_suffix: str, status: int, body: str) -> None:
        self.responses.append(("execute_raw", url_suffix, status, body))

    def _pop(
        self, channel: str, url: str
    ) -> HttpResponse:
        for idx, (ch, suffix, status, body) in enumerate(self.responses):
            if ch == channel and suffix in url:
                self.responses.pop(idx)
                return HttpResponse(status_code=status, body=body)
        raise AssertionError(f"未配置响应: channel={channel} url={url}")

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[str],
    ) -> HttpResponse:
        self.calls.append(("execute", method, url, headers, body))
        if "/api/common/openApi/getAccessKey" in url:
            ak = self.access_keys.pop(0) if self.access_keys else "ak-default"
            payload = json.dumps(
                {"code": 200, "msg": "ok", "data": {"accessKey": ak, "expiresIn": 7200}}
            )
            return HttpResponse(status_code=200, body=payload)
        return self._pop("execute", url)

    def execute_raw(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        body: Optional[bytes],
    ) -> HttpResponse:
        self.calls.append(("execute_raw", method, url, headers, body))
        return self._pop("execute_raw", url)


def _ok(data) -> str:
    return json.dumps({"code": 200, "msg": "ok", "data": data})


def _build_client(req: ImageScriptedRequester) -> PushPlusClient:
    return (
        PushPlusClient.builder()
        .token("user-token")
        .secret_key("secret")
        .http_requester(req)
        .build()
    )


def test_get_upload_token_returns_qiniu_info():
    req = ImageScriptedRequester()
    req.push(
        "/api/open/userImage/uploadToken",
        200,
        _ok(
            {
                "uploadToken": "qiniu-token",
                "uploadHost": "https://upload.qiniup.com",
                "uploadUrl": "https://upload.qiniup.com/",
                "bucket": "pushplus-img",
                "expiresIn": 600,
            }
        ),
    )
    client = _build_client(req)
    token = client.image.get_upload_token()
    assert isinstance(token, ImageUploadToken)
    assert token.uploadToken == "qiniu-token"
    assert token.uploadUrl == "https://upload.qiniup.com/"
    assert token.bucket == "pushplus-img"
    assert token.expiresIn == 600
    # 应携带 access-key
    headers = req.calls[1][3]
    assert headers and headers.get("access-key") == "ak-1"


def test_upload_bytes_posts_multipart_to_qiniu_without_access_key():
    req = ImageScriptedRequester()
    req.push(
        "/api/open/userImage/uploadToken",
        200,
        _ok(
            {
                "uploadToken": "qiniu-token",
                "uploadUrl": "https://upload.qiniup.com/",
            }
        ),
    )
    req.push_raw(
        "upload.qiniup.com",
        200,
        json.dumps(
            {
                "errno": 0,
                "ext": ".png",
                "fname": "a.png",
                "fsize": 3,
                "hash": "H",
                "key": "1/H.png",
                "mimeType": "image/png",
                "msg": "ok",
                "thumbnail": "https://pic.pushplus.plus/1/H.png@s",
                "url": "https://pic.pushplus.plus/1/H.png@p",
            }
        ),
    )

    client = _build_client(req)
    result = client.image.upload_bytes(b"\x01\x02\x03", "a.png")
    assert isinstance(result, ImageUploadResult)
    assert result.is_success()
    assert result.url == "https://pic.pushplus.plus/1/H.png@p"
    assert result.ext == ".png"

    # 七牛云上传请求应走 execute_raw，且 body 是 bytes
    upload_call = next(c for c in req.calls if c[0] == "execute_raw")
    _, method, url, headers, body = upload_call
    assert method == "POST"
    assert "upload.qiniup.com" in url
    assert "access-key" not in (headers or {})
    ct = (headers or {}).get("Content-Type", "")
    assert ct.startswith("multipart/form-data; boundary="), ct
    assert isinstance(body, (bytes, bytearray))
    body_str = bytes(body).decode("utf-8", errors="replace")
    assert 'name="token"' in body_str
    assert "qiniu-token" in body_str
    assert 'filename="a.png"' in body_str


def test_upload_raises_when_qiniu_returns_error():
    req = ImageScriptedRequester()
    req.push(
        "/api/open/userImage/uploadToken",
        200,
        _ok({"uploadToken": "qiniu-token", "uploadUrl": "https://upload.qiniup.com/"}),
    )
    req.push_raw(
        "upload.qiniup.com",
        200,
        json.dumps({"errno": 401, "msg": "bad token"}),
    )

    client = _build_client(req)
    with pytest.raises(PushPlusError) as exc:
        client.image.upload_bytes(b"\x01", "a.png")
    assert exc.value.code == 401
    assert "bad token" in exc.value.message


def test_list_and_delete_carry_access_key():
    req = ImageScriptedRequester()
    req.push(
        "/api/open/userImage/list",
        200,
        _ok(
            {
                "pageNum": 1,
                "pageSize": 10,
                "total": 1,
                "pages": 1,
                "list": [
                    {
                        "id": 1,
                        "imgUrl": "https://pic.pushplus.plus/x.png@p",
                        "thumbnail": "https://pic.pushplus.plus/x.png@s",
                        "createTime": "2026-05-09 14:44:40",
                    }
                ],
            }
        ),
    )
    req.push("/api/open/userImage/delete", 200, _ok("执行成功"))

    client = _build_client(req)
    page = client.image.list(PageQuery.of(1, 10))
    assert page.total == 1
    assert isinstance(page.list[0], ImageItem)
    assert page.list[0].id == 1

    client.image.delete(1)
    delete_call = next(c for c in req.calls if c[0] == "execute" and "/userImage/delete" in c[2])
    _, method, url, headers, _ = delete_call
    assert method == "DELETE"
    assert "id=1" in url
    assert headers and headers.get("access-key") == "ak-1"
