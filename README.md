# perk-pushplus-python-sdk

[pushplus(推送加)](https://www.pushplus.plus) 官方接口的 Python SDK，覆盖 **消息接口** 与 **全部开放接口**。

- **消息接口**（`/send`、`/batchSend`）：单渠道 + 多渠道发送，含 Builder API。
- **开放接口**（`/api/open/...`）：用户、消息、消息 token、群组、群组用户、好友、webhook、渠道、ClawBot、功能设置、预处理信息、图片服务。
- **AccessKey 自动管理**：缓存 + 过期前自动刷新；`code=401` 自动刷新并重试一次。
- **本地限流守卫**：命中 `code=900` 后按 token 短路同 token 后续发送，避免被服务端长期封禁。
- **回调解析**：`message_complate`、`add_topic_user`、`add_friend` 三类回调统一解析。
- **类型友好**：`dataclass` + `Enum`，附带 `py.typed`。

> 接口文档：
> - 消息接口：<https://www.pushplus.plus/doc/guide/api.html>
> - 开放接口：<https://www.pushplus.plus/doc/guide/openApi.html>

## 安装

```bash
pip install perk-pushplus-sdk
```

## 快速开始

### 1. 构建客户端

```python
from perk_pushplus import PushPlusClient

client = (
    PushPlusClient.builder()
    .token("your_user_token")          # 个人中心 -> 一对一推送
    .secret_key("your_secret_key")     # 个人中心 -> 开发设置（开放接口必填）
    .build()
)
```

> `PushPlusClient` 线程安全，建议作为单例长期持有。

### 2. 发送消息

```python
from perk_pushplus import Channel, SendRequest, Template

# 最简：默认 wechat / html
short_code = client.send_simple("标题", "<b>内容</b>")

# 完整：使用 Builder
short_code = client.send(
    SendRequest.builder()
    .title("CPU 告警")
    .content("# CPU > 90%\n请尽快处理")
    .template(Template.MARKDOWN)
    .channel(Channel.WECHAT)
    .topic("ops")
    .callback_url("https://your.host/pushplus/callback")
    .build()
)
```

### 3. 多渠道发送

```python
from perk_pushplus import BatchSendRequest, Channel

results = client.batch_send(
    BatchSendRequest.builder()
    .title("多渠道告警")
    .content("CPU > 90%")
    .channel(Channel.WECHAT).option("")
    .channel(Channel.WEBHOOK).option("bark")
    .channel(Channel.EXTENSION).option("")
    .build()
)
for r in results:
    print(r.channel, r.shortCode, r.code, r.message)
```

### 4. 开放接口

```python
# 用户
info = client.user.my_info()
limit = client.user.get_limit_time()

# 消息
page = client.open_message.list()
result = client.open_message.query_result("short-code")

# 消息 token
from perk_pushplus import MessageTokenAddRequest
new_token = client.message_token.add(MessageTokenAddRequest(name="for-jenkins"))

# 群组
from perk_pushplus import TopicListQuery
topics = client.topic.list(TopicListQuery.of(1, 20, topic_type=0))
detail = client.topic.detail(topic_id=123)

# 好友
qr = client.friend.get_qr_code(content="welcome")
friends = client.friend.list()

# webhook 渠道
webhooks = client.webhook.list()

# 设置
client.setting.change_is_send(1)  # 启用发送

# 预处理（会员）
client.pre.test(...)

# 图片服务（一行上传到 PushPlus 图床）
r = client.image.upload_file("/tmp/logo.png")
print(r.url)  # 可访问的图片地址
imgs = client.image.list(PageQuery.of(1, 10))
client.image.delete(imgs.list[0].id)
```

### 图片服务

PushPlus 基于七牛云提供图片图床（30 天有效，可主动删除）。SDK 把「获取上传凭证 → multipart 表单上传 → 解析 URL」封装成一步：

```python
from pathlib import Path
from perk_pushplus import ImageUploadToken, PageQuery

# 1) 最常用：一行上传本地文件，得到可访问的图片 URL
r = client.image.upload_file(Path("/tmp/logo.png"))
print(r.url)

# 2) 直接上传字节数组
client.image.upload_bytes(b"...", "screenshot.png")

# 3) 上传二进制流
with open("/tmp/a.png", "rb") as fp:
    client.image.upload_stream(fp, "a.png")

# 4) 已上传图片列表
page = client.image.list(PageQuery.of(1, 10))

# 5) 主动删除（未删除的图片默认 30 天后由系统自动清理）
client.image.delete(page.list[0].id)
```

如需自行控制凭证获取与上传过程（例如缓存 token、分布式上传）：

```python
token: ImageUploadToken = client.image.get_upload_token()
result = client.image.upload(token, b"...bytes...", "a.png", "image/png")
```

> 上传图片的真正请求会按七牛云规范以 `multipart/form-data` 提交到 `uploadUrl`，**不会**携带 PushPlus 的 `access-key`；其余三个接口（获取凭证 / 列表 / 删除）走 PushPlus 开放接口，自动带上 `access-key`。

### 5. 异步发送

```python
fut = client.send_async(SendRequest(content="hello"))
print(fut.result(timeout=10))
```

### 6. 回调解析

```python
from perk_pushplus import CallbackEvent, callback_parser

# 在你的 web 框架（Flask/FastAPI/Django/...）的回调入口里：
def on_pushplus_callback(raw_body: str) -> str:
    payload = callback_parser.parse(raw_body)
    if payload.event is CallbackEvent.MESSAGE_COMPLETE:
        info = payload.messageInfo
        print("发送结果", info.shortCode, info.get_send_status_enum())
    elif payload.event is CallbackEvent.ADD_TOPIC_USER:
        print("新订阅", payload.topicUserInfo.openId)
    elif payload.event is CallbackEvent.ADD_FRIEND:
        print("新好友", payload.friendInfo.token, payload.qrCode)
    return "ok"
```

## 配置

`PushPlusClient.builder()` 支持的全部参数：

| 方法                                    | 默认值                       | 说明                                                   |
| ------------------------------------- | ------------------------- | ---------------------------------------------------- |
| `token(str)`                          | -                         | 用户 token 或消息 token；发送消息接口默认使用                        |
| `secret_key(str)`                     | -                         | 开放接口 secretKey                                       |
| `base_url(str)`                       | `https://www.pushplus.plus` | 服务地址                                                 |
| `connect_timeout(float)`              | `10.0` 秒                  | 连接超时                                                 |
| `read_timeout(float)`                 | `30.0` 秒                  | 读超时                                                  |
| `access_key_refresh_ahead_seconds(int)` | `300`                     | 在 AccessKey 过期前多少秒主动刷新                               |
| `log_request(bool)`                   | `False`                   | 打印 DEBUG 级请求/响应日志                                    |
| `rate_limit_guard_enabled(bool)`      | `True`                    | 是否启用本地限流守卫（命中 900 后短路）                               |
| `rate_limit_cooldown_seconds(float)`  | `None`（次日 0 点）            | 命中 900 后的本地禁推时长（秒）                                   |
| `user_agent(str)`                     | `perk-pushplus-python-sdk/<v>` | UA 头                                              |
| `http_requester(HttpRequester)`       | 内置 `requests` 实现           | 自定义 HTTP 客户端（aiohttp/httpx 等可适配）                     |

## 错误处理

所有请求异常都会抛出 `PushPlusError`：

```python
from perk_pushplus import ErrorCode, PushPlusError

try:
    client.send_simple("t", "c")
except PushPlusError as exc:
    if exc.is_rate_limited():
        print("命中 code=900，已被本地守卫拒绝")
    elif exc.error_code is ErrorCode.NOT_VERIFIED:
        print("账号未实名")
    else:
        print(exc.code, exc.message)
```

`PushPlusError` 暴露：

- `code`：业务 code 或 HTTP 状态码
- `message`：错误描述
- `error_code` -> `ErrorCode` 枚举
- `is_rate_limited()`：是否为 `code=900`

## 自定义 HTTP 客户端

实现 `HttpRequester`（`Protocol`）即可：

```python
from perk_pushplus import HttpRequester, HttpResponse

class MyRequester(HttpRequester):
    def execute(self, method, url, headers, body) -> HttpResponse:
        ...

client = PushPlusClient.builder().http_requester(MyRequester()).build()
```

## 兼容性

- Python `>= 3.8`
- 仅依赖 `requests`

## 许可证

Apache License 2.0
