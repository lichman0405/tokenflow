# OAuth Library - Design Document

[English](design_EN.md) | [中文](design_CN.md)

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

## 1. Project Overview

This is a multi-language OAuth authentication library specifically designed to provide Device Flow authentication for GitHub Copilot and Hyper services. The project implements the standard OAuth2.0 Device Authorization Grant (RFC 8628) and provides specialized integration modules for two different services.

**Supported Languages**:
- **Go** - Original implementation, located in `go/` directory
- **Python** - Located in `python/` directory  
- **TypeScript** - Located in `ts/` directory

### 1.1 Core Values

- **Unified Token Management**: Provides unified token data structure and lifecycle management
- **Multi-Service Support**: Supports both GitHub Copilot and Hyper authentication scenarios
- **Automatic Refresh**: Built-in token expiration detection and automatic refresh logic
- **Device Flow Authentication**: Enables user authorization without a browser (suitable for CLI tools)
- **Multi-Language Support**: Complete implementations in Go, Python, and TypeScript

### 1.2 Project Structure

```
oauth/
├── docs/
│   ├── design_EN.md       # English design document
│   └── design_CN.md       # Chinese design document
├── go/                     # Go implementation
│   ├── go.mod
│   ├── README_EN.md
│   ├── README_CN.md
│   ├── token.go
│   ├── copilot/
│   │   ├── oauth.go       # Device flow
│   │   ├── client.go      # Custom HTTP client
│   │   ├── disk.go        # Disk cache
│   │   ├── http.go        # HTTP headers
│   │   └── urls.go        # URL constants
│   └── hyper/
│       └── device.go      # Hyper device flow
├── python/                 # Python implementation
│   ├── setup.py
│   ├── requirements.txt
│   ├── README_EN.md
│   ├── README_CN.md
│   └── oauth/
│       ├── token.py
│       ├── copilot/
│       └── hyper/
└── ts/                     # TypeScript implementation
    ├── package.json
    ├── tsconfig.json
    ├── README_EN.md
    ├── README_CN.md
    └── src/
        ├── token.ts
        ├── copilot/
        └── hyper/
```

## 2. Architecture Design

### 2.1 Layered Architecture

```
┌──────────────────────────────────────────┐
│      Application Layer (CLI/Service)     │
├──────────────────────────────────────────┤
│   copilot/        │      hyper/          │  ← Service Adapter Layer
├───────────────────┼──────────────────────┤
│          Token Management (Core)         │  ← Core Layer
├──────────────────────────────────────────┤
│      HTTP Client / Transport Layer       │
└──────────────────────────────────────────┘
```

### 2.2 Module Design

**Core Module (Token Management)**
- Language-agnostic token data structure
- Lifecycle management (creation, expiration check, refresh)
- Serialization/deserialization support

**Service Adapter Layer**
- `copilot/`: GitHub Copilot-specific implementation
- `hyper/`: Hyper service-specific implementation

**Transport Layer**
- Standard HTTP client with timeout
- Custom interceptors (e.g., X-Initiator header injection)
- Response size limiting (1MB max)

## 3. Core Design Principles

### 3.1 Token Abstraction

**Design Philosophy**: Separate token management from service-specific logic to enable reusability across different OAuth providers.

**Key Features**:
1. **Dual Time Representation**
   - `expires_in`: Relative time in seconds (for API responses)
   - `expires_at`: Absolute Unix timestamp (for expiration checks)
   - Automatic conversion between the two

2. **Smart Expiration Detection**
   - 10% buffer before actual expiration
   - Prevents using tokens near their expiration time
   - Provides time for token refresh

3. **Serialization Support**
   - Go: JSON tags for `encoding/json`
   - Python: `to_dict()` and `from_dict()` methods
   - TypeScript: `toJSON()` and `fromJSON()` methods

### 3.2 GitHub Copilot Integration

**Three-Stage Authentication Flow**:

```
1. Device Code Request
   ↓
   GitHub returns device_code and user_code
   ↓
2. User Authorization
   User visits GitHub and enters user_code
   ↓
3. Token Polling
   App polls GitHub for access token
   ↓
4. Copilot Token Exchange
   Exchange GitHub token for Copilot token
```

**Key Design Decisions**:

1. **Disk Cache Reading**
   - Reads tokens from official GitHub Copilot client cache
   - Platform-specific paths:
     - Windows: `%LOCALAPPDATA%/github-copilot/apps.json`
     - macOS/Linux: `~/.config/github-copilot/apps.json`
   - Graceful fallback if cache unavailable

2. **X-Initiator Header Injection**
   - Custom HTTP client/adapter that inspects request body
   - Sets `X-Initiator: user` for user-initiated requests
   - Sets `X-Initiator: agent` for agent/assistant messages
   - Uses regex pattern matching to detect assistant messages

3. **Error Handling**
   - Specific error for "Copilot not available" (HTTP 403)
   - Retry logic for `authorization_pending`
   - Backoff for `slow_down` errors (increments interval by 5s)

### 3.3 Hyper Service Integration

**Device Flow with Callbacks**:

```
1. Initiate Device Auth
   ↓
   Hyper returns device_code, user_code, verification_url
   ↓
2. User Authorization
   User visits verification_url and enters user_code
   ↓
3. Token Polling
   Poll until authorization complete
   ↓
4. Success Callback (optional)
   Trigger callback with user ID
   ↓
5. Token Exchange
   Exchange refresh token for access token
```

**Key Features**:

1. **Environment Configuration**
   - Base URL configurable via `HYPER_BASE_URL` environment variable
   - Default: `https://api.hyper.example.com`

2. **Token Introspection**
   - Implements RFC 7662 (OAuth 2.0 Token Introspection)
   - Validates token status and retrieves metadata
   - Returns user ID, organization ID, expiration time

3. **Success Callbacks**
   - Optional callback function/lambda on successful authentication
   - Receives user ID as parameter
   - Useful for analytics and logging

### 3.4 Security Measures

All implementations include:

1. **Request Timeouts**
   - 30-second timeout for all HTTP requests
   - Prevents hanging connections

2. **Response Size Limits**
   - Maximum 1MB response body
   - Prevents memory exhaustion attacks
   - Implemented using streaming readers

3. **Token Refresh Strategy**
   - Tokens refreshed at 90% of their lifetime
   - 10% buffer prevents edge-case failures
   - Automatic refresh on `isExpired()` check

4. **Error Handling**
   - Specific exception types for different error scenarios
   - Proper HTTP status code handling
   - Graceful degradation when optional features unavailable

## 4. Implementation Differences

### 4.1 Go Implementation

**Characteristics**:
- Uses standard library `net/http`
- Context-based cancellation and timeouts
- Interface-based design for extensibility
- No external dependencies for core functionality

**Code Style**:
```go
// Context throughout
func RequestDeviceCode(ctx context.Context) (*DeviceCode, error)

// Explicit error handling
if err != nil {
    return nil, fmt.Errorf("request failed: %w", err)
}

// Defer for cleanup
defer resp.Body.Close()
```

### 4.2 Python Implementation

**Characteristics**:
- Uses `requests` library for HTTP
- Dataclasses for structured data
- Type hints for better IDE support
- Pythonic error handling

**Code Style**:
```python
# Dataclasses
@dataclass
class Token:
    access_token: str
    refresh_token: str

# Type hints
def request_device_code(timeout: int = 30) -> DeviceCode:

# Context managers
with requests.Session() as session:
    response = session.post(url)
```

### 4.3 TypeScript Implementation

**Characteristics**:
- Uses `axios` for HTTP requests
- Full TypeScript type safety
- Async/await for all I/O operations
- ES6+ features (classes, arrow functions)

**Code Style**:
```typescript
// Class-based
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

// Promise-based
return axios.post(url, data).then(response => response.data)
```

## 5. Testing Considerations

### 5.1 Unit Testing

**Token Management**:
- Test expiration calculation
- Test 10% buffer logic
- Test serialization/deserialization

**HTTP Mocking**:
- Mock device code requests
- Mock token polling responses
- Test retry and backoff logic

### 5.2 Integration Testing

**End-to-End Flows**:
- Complete device flow authentication
- Token refresh scenarios
- Error handling paths

**Environment Testing**:
- Test disk cache reading on different platforms
- Test environment variable configuration
- Test timeout and size limit enforcement

## 6. Future Enhancements

### 6.1 Potential Features

1. **Token Storage**
   - Secure token storage (keychain/keyring integration)
   - Encrypted cache files
   - Memory-only mode for sensitive environments

2. **Additional OAuth Providers**
   - Generic OAuth2 device flow client
   - Support for other services using device flow

3. **Improved Observability**
   - Structured logging
   - Metrics/telemetry hooks
   - Debug mode with request/response logging

4. **Rate Limiting**
   - Client-side rate limiting
   - Respect `Retry-After` headers
   - Exponential backoff improvements

### 6.2 Performance Optimizations

1. **Connection Pooling**
   - Reuse HTTP connections
   - Connection keep-alive

2. **Caching**
   - Cache device codes
   - Cache user codes for retry scenarios

## 7. Best Practices for Users

### 7.1 Error Handling

Always handle specific errors:

```python
try:
    token = poll_for_token(device_code)
except NotAvailableError:
    print("GitHub Copilot not available for this account")
except TimeoutError:
    print("Authentication timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 7.2 Token Management

Check expiration before use:

```typescript
if (token.isExpired()) {
  token = await refreshToken(token.refreshToken);
}
// Use token
await makeAuthenticatedRequest(token.accessToken);
```

### 7.3 Configuration

Use environment variables for configuration:

```bash
export HYPER_BASE_URL=https://api.hyper.example.com
```

## Author

- **Name**: Shibo Li
- **Email**: shadow.li981@gmail.com

## References

This project is inspired by and references:
- [charmbracelet/crush](https://github.com/charmbracelet/crush)
- [RFC 8628 - OAuth 2.0 Device Authorization Grant](https://tools.ietf.org/html/rfc8628)
- [RFC 7662 - OAuth 2.0 Token Introspection](https://tools.ietf.org/html/rfc7662)

## License

MIT License
