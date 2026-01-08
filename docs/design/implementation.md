# Implementation Details

Deep dive into TokenFlow's implementation across languages.

## Architecture Overview

TokenFlow follows a modular architecture:

```
┌─────────────────┐
│  Token Manager  │  ← Core token lifecycle
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Copilot│ │ Hyper │  ← Service-specific implementations
└───────┘ └───────┘
```

## Language-Specific Implementations

### Go Implementation

**Philosophy**: Idiomatic Go with standard library

**Key Design Decisions**:

1. **Context-based cancellation**
   ```go
   func PollForToken(ctx context.Context, ...) (*Token, error)
   ```

2. **No external dependencies** for core functionality

3. **Struct-based API**
   ```go
   type Token struct {
       AccessToken  string
       TokenType    string
       ExpiresIn    int
       // ...
   }
   ```

4. **Error handling** via return values

### Python Implementation

**Philosophy**: Async-first with type hints

**Key Design Decisions**:

1. **Async/await** for all I/O operations
   ```python
   async def poll_for_token(device_code: DeviceCode) -> Token
   ```

2. **Dataclasses** for structured data
   ```python
   @dataclass
   class Token:
       access_token: str
       token_type: str
       expires_in: int
   ```

3. **Type hints** throughout

4. **Requests library** for HTTP (with custom adapter)

### TypeScript Implementation

**Philosophy**: Type-safe with modern async patterns

**Key Design Decisions**:

1. **Promises** for async operations
   ```typescript
   async function pollForToken(deviceCode: DeviceCode): Promise<Token>
   ```

2. **Classes** for data structures
   ```typescript
   class Token {
       constructor(data: TokenData) { ... }
   }
   ```

3. **Axios** for HTTP client

4. **Strict TypeScript** mode enabled

## HTTP Client Design

### Custom Headers

All implementations inject custom headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Initiator` | `vscode` | Identify as VS Code |
| `User-Agent` | `TokenFlow/1.0` | Library identification |
| `Accept` | `application/json` | Response format |

### Timeout Handling

30-second timeout for all requests:

=== "Go"
    ```go
    client := &http.Client{
        Timeout: 30 * time.Second,
    }
    ```

=== "Python"
    ```python
    response = session.get(url, timeout=30)
    ```

=== "TypeScript"
    ```typescript
    axios.get(url, { timeout: 30000 })
    ```

### Response Size Limiting

1MB response size limit to prevent memory exhaustion:

=== "Go"
    ```go
    const maxResponseSize = 1024 * 1024
    reader := io.LimitReader(resp.Body, maxResponseSize)
    ```

=== "Python"
    ```python
    MAX_RESPONSE_SIZE = 1024 * 1024
    for chunk in response.iter_content(chunk_size=8192):
        if total_size > MAX_RESPONSE_SIZE:
            raise ValueError("Response too large")
    ```

=== "TypeScript"
    ```typescript
    const MAX_RESPONSE_SIZE = 1024 * 1024;
    if (response.data.length > MAX_RESPONSE_SIZE) {
        throw new Error("Response too large");
    }
    ```

## Token Expiration Logic

### Buffer Calculation

10% buffer before actual expiration:

```python
def is_expired(self) -> bool:
    buffer = self.expires_in * 0.1
    return datetime.now() >= (self.expires_at - timedelta(seconds=buffer))
```

**Rationale**: Prevents race conditions where token expires during request.

**Example**:
- Token expires in 3600 seconds
- Buffer = 360 seconds (10%)
- Token considered expired after 3240 seconds

## Polling Strategy

### Initial Interval

Use server-provided interval from device code response:

```python
interval = device_code.interval  # Usually 5 seconds
```

### Slow Down Handling

Increment interval by 5 seconds on `slow_down` error:

```python
if error == "slow_down":
    interval += 5
    continue
```

### Maximum Attempts

Poll until:
- Success (token received)
- Device code expires (typically 15 minutes)
- User denies authorization
- Fatal error occurs

## Disk Cache Format

### GitHub Copilot Cache

Location: `~/.config/github-copilot/hosts.json` (Linux/macOS)

Structure:
```json
{
  "github.com": {
    "oauth_token": "gho_...",
    "user": "username"
  }
}
```

### TokenFlow Cache

Simple JSON format:
```json
{
  "access_token": "gho_...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "expires_at": "2026-01-08T12:00:00Z"
}
```

## Testing Strategy

### Unit Tests

Mock HTTP responses:

```python
@pytest.fixture
def mock_device_code():
    return DeviceCode(
        device_code="test_device_code",
        user_code="TEST-1234",
        verification_uri="https://github.com/login/device",
        interval=5
    )
```

### Integration Tests

Test against real services (with valid credentials):

```python
@pytest.mark.integration
async def test_full_flow():
    device_code = await initiate_device_flow()
    # Manual authorization required
    token = await poll_for_token(device_code)
    assert token.access_token
```

## Performance Considerations

### Memory Usage

- Token objects: ~200 bytes
- HTTP responses limited to 1MB
- Streaming JSON parsing where possible

### Network Efficiency

- Connection reuse via HTTP clients
- Gzip compression support
- Minimal request payloads

### CPU Usage

- Polling intervals respect server limits
- No busy waiting
- Efficient JSON parsing

## Future Enhancements

Planned improvements:

1. **Refresh token support** - Automatic token refresh without re-authentication
2. **Token encryption** - Encrypt cached tokens at rest
3. **Multiple service support** - Generalized OAuth flow for any service
4. **Rate limiting** - Built-in rate limit handling
5. **Metrics** - Optional telemetry for usage tracking
