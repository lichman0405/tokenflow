# TokenFlow

[![GitHub](https://img.shields.io/badge/GitHub-tokenflow-blue?logo=github)](https://github.com/lichman0405/tokenflow)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](license.md)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue)](https://lichman0405.github.io/tokenflow/)

!!! warning "Important Notice"
    This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

**TokenFlow** is a multi-language OAuth2 Device Flow implementation supporting GitHub Copilot and Hyper services.

## Features

### GitHub Copilot Integration

- ✅ OAuth2 Device Authorization Flow (RFC 8628)
- ✅ Token caching from official Copilot client
- ✅ Custom HTTP client with X-Initiator header injection
- ✅ Automatic token refresh

### Hyper Integration

- ✅ Device authorization flow
- ✅ Token exchange
- ✅ Token introspection (RFC 7662)
- ✅ Configurable base URL via environment variable

### Token Management

- ✅ Unified token structure across all implementations
- ✅ Automatic expiration calculation
- ✅ 10% buffer for token refresh
- ✅ JSON serialization support

## Language Implementations

TokenFlow is available in three languages:

=== "Go"

    ```bash
    go get github.com/lichman0405/tokenflow/go
    ```

    [Go Documentation](usage/go.md){ .md-button }

=== "Python"

    ```bash
    pip install tokenflow
    ```

    [Python Documentation](usage/python.md){ .md-button }

=== "TypeScript"

    ```bash
    npm install tokenflow
    ```

    [TypeScript Documentation](usage/typescript.md){ .md-button }

## Security

All implementations include:

- ⏱️ 30-second HTTP request timeouts
- 📏 1MB response size limits
- 🔄 Token refresh before expiration

## Quick Links

- [Getting Started](getting-started/installation.md) - Installation instructions
- [Usage Guide](usage/index.md) - Comprehensive examples
- [API Reference](api/token.md) - Detailed API documentation
- [Design](design/architecture.md) - Architecture and implementation details

## Author

**Shibo Li**  
📧 [shadow.li981@gmail.com](mailto:shadow.li981@gmail.com)

## References

This project is inspired by:

- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## License

MIT License - see [LICENSE](license.md) for details.
