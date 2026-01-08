# OAuth 库

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **警告**：此库可能违反 GitHub Copilot 的服务条款。使用此库在未获得适当授权的情况下访问 GitHub Copilot 可能导致账号被暂停或终止。本项目仅供教育和研究目的使用。使用风险自负，请确保在使用此库之前获得适当的授权。

多语言实现的 OAuth2 设备授权流程库，支持 GitHub Copilot 和 Hyper 服务。

## 语言实现

| 语言 | 目录 | 文档 |
|------|------|------|
| Go | [go/](go/) | [English](go/README_EN.md) / [中文](go/README_CN.md) |
| Python | [python/](python/) | [English](python/README_EN.md) / [中文](python/README_CN.md) |
| TypeScript | [ts/](ts/) | [English](ts/README_EN.md) / [中文](ts/README_CN.md) |

## 功能特性

### GitHub Copilot 集成

- OAuth2 设备授权流程 (RFC 8628)
- 从官方 Copilot 客户端读取缓存 Token
- 自定义 HTTP 客户端，注入 X-Initiator 请求头
- Token 刷新支持

### Hyper 集成

- 设备授权流程
- Token 交换
- Token 内省 (RFC 7662)
- 通过环境变量配置基础 URL

### Token 管理

- 所有实现统一的 Token 结构
- 自动过期时间计算
- 10% 的刷新缓冲
- JSON 序列化支持

## 安全性

所有实现都包含：
- 30 秒 HTTP 请求超时
- 1MB 响应大小限制
- Token 过期前刷新

## 快速开始

### Go

```bash
cd go
go build ./...
```

详细使用方法请参阅 [Go 文档](go/README_CN.md)。

### Python

```bash
cd python
pip install -e .
```

详细使用方法请参阅 [Python 文档](python/README_CN.md)。

### TypeScript

```bash
cd ts
npm install
npm run build
```

详细使用方法请参阅 [TypeScript 文档](ts/README_CN.md)。

## 设计文档

详细的设计思路和架构请参阅 [docs/design.md](docs/design.md)。

## 作者

- **姓名**：Shibo Li
- **邮箱**：shadow.li981@gmail.com

## 参考来源

本项目受以下项目启发并参考：
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## 许可证

MIT License
