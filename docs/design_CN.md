# OAuth 库 - 设计文档

[English](design_EN.md) | [中文](design_CN.md)

> ⚠️ **警告**：此库可能违反 GitHub Copilot 的服务条款。使用此库在未获得适当授权的情况下访问 GitHub Copilot 可能导致账号被暂停或终止。本项目仅供教育和研究目的使用。使用风险自负，请确保在使用此库之前获得适当的授权。

## 1. 项目概述

这是一个多语言 OAuth 认证库，专门为 GitHub Copilot 和 Hyper 服务提供设备流（Device Flow）认证支持。项目实现了标准的 OAuth2.0 设备授权流程（RFC 8628），并为两个不同的服务提供了专门的集成模块。

**支持的语言**：
- **Go** - 原始实现，位于 `go/` 目录
- **Python** - 位于 `python/` 目录
- **TypeScript** - 位于 `ts/` 目录

### 1.1 核心价值

- **统一的 Token 管理**：提供统一的 Token 数据结构和生命周期管理
- **多服务支持**：同时支持 GitHub Copilot 和 Hyper 两种不同的认证场景
- **自动刷新机制**：内置 Token 过期检测和自动刷新逻辑
- **设备流认证**：实现无浏览器环境下的用户授权（适合 CLI 工具）
- **多语言支持**：提供 Go、Python、TypeScript 三种语言的完整实现

### 1.2 项目结构

```
oauth/
├── docs/
│   ├── design_EN.md       # 英文设计文档
│   └── design_CN.md       # 中文设计文档
├── go/                     # Go 实现
│   ├── go.mod
│   ├── README_EN.md
│   ├── README_CN.md
│   ├── token.go
│   ├── copilot/
│   │   ├── oauth.go       # 设备流程
│   │   ├── client.go      # 自定义 HTTP 客户端
│   │   ├── disk.go        # 磁盘缓存
│   │   ├── http.go        # HTTP 请求头
│   │   └── urls.go        # URL 常量
│   └── hyper/
│       └── device.go      # Hyper 设备流程
├── python/                 # Python 实现
│   ├── setup.py
│   ├── requirements.txt
│   ├── README_EN.md
│   ├── README_CN.md
│   └── oauth/
│       ├── token.py
│       ├── copilot/
│       └── hyper/
└── ts/                     # TypeScript 实现
    ├── package.json
    ├── tsconfig.json
    ├── README_EN.md
    ├── README_CN.md
    └── src/
        ├── token.ts
        ├── copilot/
        └── hyper/
```

## 2. 架构设计

### 2.1 分层架构

```
┌──────────────────────────────────────────┐
│        应用层 (CLI/服务)                  │
├──────────────────────────────────────────┤
│   copilot/        │      hyper/          │  ← 服务适配层
├───────────────────┼──────────────────────┤
│          Token 管理 (核心层)              │  ← 核心层
├──────────────────────────────────────────┤
│      HTTP 客户端 / 传输层                 │
└──────────────────────────────────────────┘
```

### 2.2 模块设计

**核心模块（Token 管理）**
- 语言无关的 Token 数据结构
- 生命周期管理（创建、过期检查、刷新）
- 序列化/反序列化支持

**服务适配层**
- `copilot/`：GitHub Copilot 特定实现
- `hyper/`：Hyper 服务特定实现

**传输层**
- 标准 HTTP 客户端（带超时）
- 自定义拦截器（如 X-Initiator 请求头注入）
- 响应大小限制（最大 1MB）

## 3. 核心设计原则

### 3.1 Token 抽象

**设计哲学**：将 Token 管理与服务特定逻辑分离，实现跨不同 OAuth 提供商的可复用性。

**关键特性**：
1. **双时间表示**
   - `expires_in`：相对时间（秒），用于 API 响应
   - `expires_at`：绝对 Unix 时间戳，用于过期检查
   - 两者之间自动转换

2. **智能过期检测**
   - 实际过期前 10% 的缓冲
   - 防止使用即将过期的 Token
   - 为 Token 刷新提供时间

3. **序列化支持**
   - Go: JSON 标签用于 `encoding/json`
   - Python: `to_dict()` 和 `from_dict()` 方法
   - TypeScript: `toJSON()` 和 `fromJSON()` 方法

### 3.2 GitHub Copilot 集成

**三阶段认证流程**：

```
1. 设备码请求
   ↓
   GitHub 返回 device_code 和 user_code
   ↓
2. 用户授权
   用户访问 GitHub 并输入 user_code
   ↓
3. Token 轮询
   应用轮询 GitHub 获取访问令牌
   ↓
4. Copilot Token 交换
   用 GitHub token 交换 Copilot token
```

**关键设计决策**：

1. **磁盘缓存读取**
   - 从官方 GitHub Copilot 客户端缓存读取 Token
   - 平台特定路径：
     - Windows: `%LOCALAPPDATA%/github-copilot/apps.json`
     - macOS/Linux: `~/.config/github-copilot/apps.json`
   - 缓存不可用时优雅降级

2. **X-Initiator 请求头注入**
   - 自定义 HTTP 客户端/适配器检查请求体
   - 用户发起的请求设置 `X-Initiator: user`
   - Agent/助手消息设置 `X-Initiator: agent`
   - 使用正则表达式匹配检测助手消息

3. **错误处理**
   - "Copilot 不可用"的特定错误（HTTP 403）
   - `authorization_pending` 的重试逻辑
   - `slow_down` 错误的退避（间隔增加 5 秒）

### 3.3 Hyper 服务集成

**带回调的设备流程**：

```
1. 发起设备授权
   ↓
   Hyper 返回 device_code, user_code, verification_url
   ↓
2. 用户授权
   用户访问 verification_url 并输入 user_code
   ↓
3. Token 轮询
   轮询直到授权完成
   ↓
4. 成功回调（可选）
   触发回调，传入用户 ID
   ↓
5. Token 交换
   用刷新令牌交换访问令牌
```

**关键特性**：

1. **环境配置**
   - 基础 URL 可通过 `HYPER_BASE_URL` 环境变量配置
   - 默认值：`https://api.hyper.example.com`

2. **Token 内省**
   - 实现 RFC 7662（OAuth 2.0 Token Introspection）
   - 验证 Token 状态并获取元数据
   - 返回用户 ID、组织 ID、过期时间

3. **成功回调**
   - 认证成功时可选的回调函数/lambda
   - 接收用户 ID 作为参数
   - 用于分析和日志记录

### 3.4 安全措施

所有实现都包含：

1. **请求超时**
   - 所有 HTTP 请求 30 秒超时
   - 防止连接挂起

2. **响应大小限制**
   - 最大 1MB 响应体
   - 防止内存耗尽攻击
   - 使用流式读取器实现

3. **Token 刷新策略**
   - Token 在生命周期的 90% 时刷新
   - 10% 缓冲防止边界情况失败
   - `isExpired()` 检查时自动刷新

4. **错误处理**
   - 不同错误场景的特定异常类型
   - 正确的 HTTP 状态码处理
   - 可选功能不可用时优雅降级

## 4. 实现差异

### 4.1 Go 实现

**特点**：
- 使用标准库 `net/http`
- 基于 Context 的取消和超时
- 基于接口的可扩展设计
- 核心功能无外部依赖

**代码风格**：
```go
// Context 贯穿始终
func RequestDeviceCode(ctx context.Context) (*DeviceCode, error)

// 显式错误处理
if err != nil {
    return nil, fmt.Errorf("request failed: %w", err)
}

// 使用 defer 清理
defer resp.Body.Close()
```

### 4.2 Python 实现

**特点**：
- 使用 `requests` 库处理 HTTP
- Dataclass 用于结构化数据
- 类型提示提供更好的 IDE 支持
- Pythonic 错误处理

**代码风格**：
```python
# Dataclass
@dataclass
class Token:
    access_token: str
    refresh_token: str

# 类型提示
def request_device_code(timeout: int = 30) -> DeviceCode:

# 上下文管理器
with requests.Session() as session:
    response = session.post(url)
```

### 4.3 TypeScript 实现

**特点**：
- 使用 `axios` 处理 HTTP 请求
- 完整的 TypeScript 类型安全
- 所有 I/O 操作使用 async/await
- ES6+ 特性（类、箭头函数）

**代码风格**：
```typescript
// 基于类
class Token {
  constructor(
    public accessToken: string,
    public refreshToken: string,
    public expiresIn: number,
    public expiresAt: number
  ) {}
}

// Async/await
async function requestDeviceCode(timeout: number = 30000): Promise<DeviceCode>

// 基于 Promise
return axios.post(url, data).then(response => response.data)
```

## 5. 测试考虑

### 5.1 单元测试

**Token 管理**：
- 测试过期计算
- 测试 10% 缓冲逻辑
- 测试序列化/反序列化

**HTTP 模拟**：
- 模拟设备码请求
- 模拟 Token 轮询响应
- 测试重试和退避逻辑

### 5.2 集成测试

**端到端流程**：
- 完整的设备流认证
- Token 刷新场景
- 错误处理路径

**环境测试**：
- 测试不同平台上的磁盘缓存读取
- 测试环境变量配置
- 测试超时和大小限制强制执行

## 6. 未来增强

### 6.1 潜在功能

1. **Token 存储**
   - 安全 Token 存储（钥匙串/密钥环集成）
   - 加密缓存文件
   - 敏感环境的内存模式

2. **额外的 OAuth 提供商**
   - 通用 OAuth2 设备流客户端
   - 支持其他使用设备流的服务

3. **改进的可观察性**
   - 结构化日志
   - 指标/遥测钩子
   - 带请求/响应日志的调试模式

4. **速率限制**
   - 客户端速率限制
   - 遵守 `Retry-After` 头
   - 指数退避改进

### 6.2 性能优化

1. **连接池**
   - 复用 HTTP 连接
   - 连接保持活动

2. **缓存**
   - 缓存设备码
   - 缓存用户码用于重试场景

## 7. 用户最佳实践

### 7.1 错误处理

始终处理特定错误：

```python
try:
    token = poll_for_token(device_code)
except NotAvailableError:
    print("GitHub Copilot 对此账户不可用")
except TimeoutError:
    print("认证超时")
except Exception as e:
    print(f"意外错误: {e}")
```

### 7.2 Token 管理

使用前检查过期：

```typescript
if (token.isExpired()) {
  token = await refreshToken(token.refreshToken);
}
// 使用 token
await makeAuthenticatedRequest(token.accessToken);
```

### 7.3 配置

使用环境变量进行配置：

```bash
export HYPER_BASE_URL=https://api.hyper.example.com
```

## 作者

- **姓名**：Shibo Li
- **邮箱**：shadow.li981@gmail.com

## 参考来源

本项目受以下项目启发并参考：
- [charmbracelet/crush](https://github.com/charmbracelet/crush)
- [RFC 8628 - OAuth 2.0 设备授权流程](https://tools.ietf.org/html/rfc8628)
- [RFC 7662 - OAuth 2.0 Token 内省](https://tools.ietf.org/html/rfc7662)

## 许可证

MIT License
