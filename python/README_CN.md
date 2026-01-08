# OAuth 设备流认证库 (Python)

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **警告**：此库可能违反 GitHub Copilot 的服务条款。使用此库在未获得适当授权的情况下访问 GitHub Copilot 可能导致账号被暂停或终止。本项目仅供教育和研究目的使用。使用风险自负，请确保在使用此库之前获得适当的授权。

## 概述

OAuth2 设备流认证的 Python 实现，支持 GitHub Copilot 和 Hyper 服务集成。

## 特性

- ✅ **设备流认证**：实现 OAuth2 设备授权流程
- ✅ **Token 生命周期管理**：自动过期检测和刷新
- ✅ **多服务支持**：GitHub Copilot 和 Hyper 服务适配器
- ✅ **磁盘缓存**：从官方 GitHub Copilot 客户端缓存读取 Token
- ✅ **类型提示**：完整的类型注解支持
- ✅ **错误处理**：全面的错误处理和重试机制

## 安装

```bash
pip install -r requirements.txt
```

或以开发模式安装：

```bash
pip install -e .
```

## 快速开始

### GitHub Copilot 认证

```python
from oauth.copilot import request_device_code, poll_for_token, refresh_token_from_disk

# 尝试从磁盘缓存读取 token
github_token = refresh_token_from_disk()

if github_token:
    from oauth.copilot import refresh_token
    token = refresh_token(github_token)
else:
    # 启动设备流
    device_code = request_device_code()
    print(f"访问: {device_code.verification_uri}")
    print(f"输入代码: {device_code.user_code}")
    
    # 轮询获取 token
    token = poll_for_token(device_code)

print(f"访问令牌: {token.access_token}")
```

### Hyper 服务认证

```python
from oauth.hyper import initiate_device_auth, poll_for_token, exchange_token

# 启动设备授权
auth = initiate_device_auth()
print(f"访问: {auth.verification_url}")
print(f"输入代码: {auth.user_code}")

# 轮询获取刷新令牌
refresh_token = poll_for_token(auth.device_code, auth.expires_in)

# 交换访问令牌
token = exchange_token(refresh_token)

# 检查 token 是否过期
if token.is_expired():
    token = exchange_token(refresh_token)
```

## 模块结构

```
oauth/
├── __init__.py          # 包初始化
├── token.py             # Token 数据结构和生命周期管理
├── copilot/             # GitHub Copilot 集成
│   ├── __init__.py
│   ├── oauth.py         # 设备流实现
│   ├── disk.py          # 磁盘缓存读取
│   ├── client.py        # 带拦截器的 HTTP 客户端
│   ├── http.py          # HTTP 请求头
│   └── urls.py          # URL 常量
└── hyper/               # Hyper 服务集成
    ├── __init__.py
    └── device.py        # 设备流实现
```

## API 参考

### Token 管理

```python
from oauth import Token

# 创建 token
token = Token(
    access_token="...",
    refresh_token="...",
    expires_in=3600
)

# 设置过期时间戳
token.set_expires_at()

# 检查是否过期（带有 10% 的缓冲）
if token.is_expired():
    # 刷新 token
    pass

# 序列化为字典
data = token.to_dict()

# 从字典反序列化
token = Token.from_dict(data)
```

### Copilot 模块

```python
from oauth.copilot import (
    request_device_code,
    poll_for_token,
    refresh_token,
    refresh_token_from_disk,
    create_client,
    NotAvailableError,
)

# 请求设备码
device_code = request_device_code(timeout=30)

# 轮询获取 token（阻塞直到授权或超时）
token = poll_for_token(device_code, timeout=600)

# 刷新 Copilot token
token = refresh_token(github_token)

# 从磁盘缓存读取
github_token = refresh_token_from_disk()

# 创建带有 X-Initiator 请求头注入的 HTTP 客户端
client = create_client(is_sub_agent=False, debug=True)
```

### Hyper 模块

```python
from oauth.hyper import (
    initiate_device_auth,
    poll_for_token,
    exchange_token,
    introspect_token,
)

# 发起设备授权
auth = initiate_device_auth(timeout=30)

# 轮询获取刷新令牌
refresh_token = poll_for_token(auth.device_code, auth.expires_in)

# 交换访问令牌
token = exchange_token(refresh_token, timeout=30)

# 内省令牌 (RFC 7662)
info = introspect_token(token.access_token)
if info.active:
    print(f"用户 ID: {info.sub}")
```

## 错误处理

```python
from oauth.copilot import NotAvailableError
import requests

try:
    token = poll_for_token(device_code)
except NotAvailableError:
    print("GitHub Copilot 对此账户不可用")
except TimeoutError:
    print("授权超时")
except requests.RequestException as e:
    print(f"网络错误: {e}")
```

## 依赖要求

- Python 3.8+
- requests >= 2.31.0

## 作者

- **姓名**：Shibo Li
- **邮箱**：shadow.li981@gmail.com

## 参考来源

本项目受以下项目启发并参考：
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## 许可证

MIT License
