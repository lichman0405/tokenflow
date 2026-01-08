# Go 语言 OAuth 库

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **警告**：此库可能违反 GitHub Copilot 的服务条款。使用此库在未获得适当授权的情况下访问 GitHub Copilot 可能导致账号被暂停或终止。本项目仅供教育和研究目的使用。使用风险自负，请确保在使用此库之前获得适当的授权。

Go 语言实现的 OAuth2 设备授权流程库，支持 GitHub Copilot 和 Hyper 服务。

## 安装

```bash
go get github.com/user/oauth
```

## 功能特性

### Token 管理

`oauth.Token` 结构体提供统一的 Token 管理：
- 自动过期时间计算
- 10% 的刷新缓冲（在实际过期前刷新）
- JSON 序列化支持

```go
import "github.com/user/oauth"

token := &oauth.Token{
    AccessToken:  "...",
    RefreshToken: "...",
    ExpiresIn:    3600,
}
token.SetExpiresAt()

if token.IsExpired() {
    // 刷新 Token
}
```

### GitHub Copilot 集成

GitHub Copilot 的设备授权流程：

```go
import (
    "context"
    "github.com/user/oauth/copilot"
)

ctx := context.Background()

// 步骤 1：请求设备码
dc, err := copilot.RequestDeviceCode(ctx)
if err != nil {
    log.Fatal(err)
}

// 显示给用户
fmt.Printf("请访问 %s 并输入代码: %s\n", dc.VerificationURI, dc.UserCode)

// 步骤 2：轮询获取 Token
token, err := copilot.PollForToken(ctx, dc)
if err != nil {
    log.Fatal(err)
}

// 步骤 3：过期时刷新
if token.IsExpired() {
    token, err = copilot.RefreshToken(ctx, token.RefreshToken)
}
```

#### 磁盘缓存

从官方 GitHub Copilot 客户端读取缓存的 Token：

```go
if refreshToken, ok := copilot.RefreshTokenFromDisk(); ok {
    token, err := copilot.RefreshToken(ctx, refreshToken)
    // 使用 token...
}
```

#### 自定义 HTTP 客户端

创建带有 X-Initiator 请求头注入的 HTTP 客户端：

```go
client := copilot.NewClient(false) // isSubAgent = false

// 客户端会根据请求体自动设置 X-Initiator 请求头
```

### Hyper 服务

Hyper 的设备授权流程：

```go
import (
    "context"
    "github.com/user/oauth/hyper"
)

ctx := context.Background()

// 步骤 1：发起设备授权
auth, err := hyper.InitiateDeviceAuth(ctx)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("请访问 %s 并输入代码: %s\n", auth.VerificationURL, auth.UserCode)

// 步骤 2：轮询获取 Token
refreshToken, err := hyper.PollForToken(ctx, auth.DeviceCode, auth.ExpiresIn, func(userID string) {
    // 可选：成功时回调，传入用户ID
    fmt.Printf("已认证用户: %s\n", userID)
})
if err != nil {
    log.Fatal(err)
}

// 步骤 3：交换访问令牌
token, err := hyper.ExchangeToken(ctx, refreshToken)
if err != nil {
    log.Fatal(err)
}

// 步骤 4：内省令牌（可选）
info, err := hyper.IntrospectToken(ctx, token.AccessToken)
if info.Active {
    fmt.Printf("Token 有效期至: %d\n", info.Exp)
}
```

#### 配置

通过环境变量设置 Hyper 基础 URL：

```bash
export HYPER_BASE_URL=https://api.hyper.example.com
```

## 项目结构

```
go/
├── go.mod              # 模块定义
├── token.go            # Token 结构体和方法
├── copilot/
│   ├── oauth.go        # Copilot 设备流程
│   ├── client.go       # 自定义 HTTP 客户端
│   ├── disk.go         # 磁盘缓存读取
│   ├── http.go         # HTTP 请求头
│   └── urls.go         # URL 常量
└── hyper/
    └── device.go       # Hyper 设备流程
```

## 安全性

- 所有 HTTP 请求都有 30 秒超时
- 响应体大小限制为 1MB 以防止内存耗尽
- Token 在实际过期前刷新（10% 缓冲）

## 作者

- **姓名**：Shibo Li
- **邮箱**：shadow.li981@gmail.com

## 参考来源

本项目受以下项目启发并参考：
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## 许可证

MIT License
