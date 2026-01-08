# OAuth 设备流认证库 (TypeScript)

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **警告**：此库可能违反 GitHub Copilot 的服务条款。使用此库在未获得适当授权的情况下访问 GitHub Copilot 可能导致账号被暂停或终止。本项目仅供教育和研究目的使用。使用风险自负，请确保在使用此库之前获得适当的授权。

## 概述

OAuth2 设备流认证的 TypeScript 实现，支持 GitHub Copilot 和 Hyper 服务集成。

## 特性

- ✅ **设备流认证**：实现 OAuth2 设备授权流程
- ✅ **Token 生命周期管理**：自动过期检测和刷新
- ✅ **多服务支持**：GitHub Copilot 和 Hyper 服务适配器
- ✅ **磁盘缓存**：从官方 GitHub Copilot 客户端缓存读取 Token
- ✅ **类型安全**：完整的 TypeScript 类型定义
- ✅ **错误处理**：全面的错误处理和重试机制
- ✅ **异步支持**：现代 async/await 编程支持

## 安装

```bash
npm install
```

## 构建

```bash
npm run build
```

## 快速开始

### GitHub Copilot 认证

```typescript
import { copilot, Token } from "oauth-deviceflow";

async function authenticate() {
  // 尝试从磁盘缓存读取 token
  const githubToken = copilot.refreshTokenFromDisk();

  let token: Token;
  if (githubToken) {
    token = await copilot.refreshToken(githubToken);
  } else {
    // 启动设备流
    const deviceCode = await copilot.requestDeviceCode();
    console.log(`访问: ${deviceCode.verificationUri}`);
    console.log(`输入代码: ${deviceCode.userCode}`);
    
    // 轮询获取 token
    token = await copilot.pollForToken(deviceCode);
  }

  console.log(`访问令牌: ${token.accessToken}`);
}

authenticate().catch(console.error);
```

### Hyper 服务认证

```typescript
import { hyper, Token } from "oauth-deviceflow";

async function authenticate() {
  // 启动设备授权
  const auth = await hyper.initiateDeviceAuth();
  console.log(`访问: ${auth.verificationUrl}`);
  console.log(`输入代码: ${auth.userCode}`);

  // 轮询获取刷新令牌
  const refreshToken = await hyper.pollForToken(auth.deviceCode, auth.expiresIn);

  // 交换访问令牌
  let token = await hyper.exchangeToken(refreshToken);

  // 检查 token 是否过期
  if (token.isExpired()) {
    token = await hyper.exchangeToken(refreshToken);
  }

  console.log(`访问令牌: ${token.accessToken}`);
}

authenticate().catch(console.error);
```

## 模块结构

```
src/
├── index.ts             # 包入口点
├── token.ts             # Token 数据结构和生命周期管理
├── copilot/             # GitHub Copilot 集成
│   ├── index.ts
│   ├── oauth.ts         # 设备流实现
│   ├── disk.ts          # 磁盘缓存读取
│   ├── client.ts        # 带拦截器的 HTTP 客户端
│   ├── http.ts          # HTTP 请求头
│   └── urls.ts          # URL 常量
└── hyper/               # Hyper 服务集成
    ├── index.ts
    └── device.ts        # 设备流实现
```

## API 参考

### Token 管理

```typescript
import { Token } from "oauth-deviceflow";

// 创建 token
const token = new Token(
  "access_token_here",
  "refresh_token_here",
  3600,
  0
);

// 设置过期时间戳
token.setExpiresAt();

// 检查是否过期（带有 10% 的缓冲）
if (token.isExpired()) {
  // 刷新 token
}

// 序列化为 JSON
const data = token.toJSON();

// 从 JSON 反序列化
const token2 = Token.fromJSON(data);
```

### Copilot 模块

```typescript
import { copilot } from "oauth-deviceflow";

// 请求设备码
const deviceCode = await copilot.requestDeviceCode(30000);

// 轮询获取 token（阻塞直到授权或超时）
const token = await copilot.pollForToken(deviceCode, 600000);

// 刷新 Copilot token
const newToken = await copilot.refreshToken(githubToken);

// 从磁盘缓存读取
const githubToken = copilot.refreshTokenFromDisk();

// 创建带有 X-Initiator 请求头注入的 HTTP 客户端
const client = copilot.createClient(false, true);
```

### Hyper 模块

```typescript
import { hyper } from "oauth-deviceflow";

// 发起设备授权
const auth = await hyper.initiateDeviceAuth(30000);

// 轮询获取刷新令牌
const refreshToken = await hyper.pollForToken(auth.deviceCode, auth.expiresIn);

// 交换访问令牌
const token = await hyper.exchangeToken(refreshToken, 30000);

// 内省令牌 (RFC 7662)
const info = await hyper.introspectToken(token.accessToken);
if (info.active) {
  console.log(`用户 ID: ${info.sub}`);
}
```

## 错误处理

```typescript
import { copilot } from "oauth-deviceflow";

try {
  const token = await copilot.pollForToken(deviceCode);
} catch (error) {
  if (error instanceof copilot.NotAvailableError) {
    console.error("GitHub Copilot 对此账户不可用");
  } else if (error.message === "Authorization timed out") {
    console.error("授权超时");
  } else {
    console.error("网络错误:", error);
  }
}
```

## 依赖要求

- Node.js 16+
- TypeScript 5.3+
- axios >= 1.6.0

## 作者

- **姓名**：Shibo Li
- **邮箱**：shadow.li981@gmail.com

## 参考来源

本项目受以下项目启发并参考：
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## 许可证

MIT License
