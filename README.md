# TokenFlow

[English](README.md) | [中文](README_CN.md)

[![GitHub](https://img.shields.io/badge/GitHub-tokenflow-blue?logo=github)](https://github.com/lichman0405/tokenflow)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

Multi-language OAuth2 Device Flow implementation for GitHub Copilot and Hyper services.

## Language Implementations

| Language | Directory | Documentation |
|----------|-----------|---------------|
| Go | [go/](go/) | [English](go/README_EN.md) / [中文](go/README_CN.md) |
| Python | [python/](python/) | [English](python/README_EN.md) / [中文](python/README_CN.md) |
| TypeScript | [ts/](ts/) | [English](ts/README_EN.md) / [中文](ts/README_CN.md) |

## Features

### GitHub Copilot Integration

- OAuth2 Device Authorization Flow (RFC 8628)
- Token caching from official Copilot client
- Custom HTTP client with X-Initiator header injection
- Token refresh support

### Hyper Integration

- Device authorization flow
- Token exchange
- Token introspection (RFC 7662)
- Configurable base URL via environment variable

### Token Management

- Unified token structure across all implementations
- Automatic expiration calculation
- 10% buffer for token refresh
- JSON serialization support

## Security

All implementations include:
- 30-second HTTP request timeouts
- 1MB response size limits
- Token refresh before expiration

## Quick Start

### Go

```bash
cd go
go build ./...
```

See [Go Documentation](go/README_EN.md) for detailed usage.

### Python

```bash
cd python
pip install -e .
```

See [Python Documentation](python/README_EN.md) for detailed usage.

### TypeScript

```bash
cd ts
npm install
npm run build
```

See [TypeScript Documentation](ts/README_EN.md) for detailed usage.

## Documentation

- **Usage Guide**: [USAGE.md](USAGE.md) - Comprehensive examples for all languages
- **Design Document**: [docs/design_EN.md](docs/design_EN.md) / [docs/design_CN.md](docs/design_CN.md)

## Author

- **Name**: Shibo Li
- **Email**: shadow.li981@gmail.com

## References

This project is inspired by and references:
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## License

MIT License
