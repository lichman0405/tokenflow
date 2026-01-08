# Hyper API

OAuth2 Device Flow implementation for Hyper service.

## Functions

### `InitiateDeviceFlow` / `initiate_device_flow`

Initiates the device authorization flow for Hyper.

**Returns**: Device code response

=== "Go"
    ```go
    func InitiateDeviceFlow(ctx context.Context) (*DeviceCodeResponse, error)
    ```

=== "Python"
    ```python
    async def initiate_device_flow() -> DeviceCode
    ```

=== "TypeScript"
    ```typescript
    async function initiateDeviceFlow(): Promise<DeviceCode>
    ```

---

### `PollForToken` / `poll_for_token`

Polls for access token after user authorization.

**Parameters**:
- `device_code`: Device code from initiation
- `on_success`: Optional callback on successful authentication

**Returns**: Access token

=== "Go"
    ```go
    func PollForToken(ctx context.Context, deviceCode *DeviceCodeResponse, 
                      onSuccess func(*Token)) (*Token, error)
    ```

=== "Python"
    ```python
    async def poll_for_token(device_code: DeviceCode, 
                            on_success: Optional[Callable] = None) -> Token
    ```

=== "TypeScript"
    ```typescript
    async function pollForToken(deviceCode: DeviceCode, 
                               onSuccess?: (token: Token) => void): Promise<Token>
    ```

---

### `IntrospectToken` / `introspect_token`

Introspects an access token to check its validity (RFC 7662).

**Parameters**:
- `token`: Access token to introspect

**Returns**: Token introspection response

=== "Go"
    ```go
    func IntrospectToken(ctx context.Context, token string) (map[string]interface{}, error)
    ```

=== "Python"
    ```python
    async def introspect_token(token: str) -> dict
    ```

=== "TypeScript"
    ```typescript
    async function introspectToken(token: string): Promise<IntrospectionResponse>
    ```

**Response Fields**:
- `active` (bool): Token validity status
- `scope` (string): Token scope
- `exp` (int): Expiration timestamp
- `iat` (int): Issued at timestamp

**Example**:

=== "Go"
    ```go
    info, err := hyper.IntrospectToken(ctx, token.AccessToken)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Active: %v\n", info["active"])
    ```

=== "Python"
    ```python
    info = await introspect_token(token.access_token)
    print(f"Active: {info['active']}")
    ```

=== "TypeScript"
    ```typescript
    const info = await introspectToken(token.accessToken);
    console.log(`Active: ${info.active}`);
    ```

---

### `BaseURL` / `base_url`

Returns the configured Hyper API base URL.

**Default**: `https://api.hyper.io`

**Environment Variable**: `HYPER_BASE_URL`

=== "Go"
    ```go
    func BaseURL() string
    ```

=== "Python"
    ```python
    def base_url() -> str
    ```

=== "TypeScript"
    ```typescript
    function baseURL(): string
    ```

**Example**:

```bash
export HYPER_BASE_URL="https://custom.hyper.io"
```

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/oauth/device` | Device code initiation |
| `/oauth/token` | Token exchange |
| `/oauth/introspect` | Token introspection |

## Configuration

### Custom Base URL

Configure via environment variable:

=== "Bash"
    ```bash
    export HYPER_BASE_URL="https://your-hyper-instance.com"
    ```

=== "PowerShell"
    ```powershell
    $env:HYPER_BASE_URL = "https://your-hyper-instance.com"
    ```

=== "Go"
    ```go
    os.Setenv("HYPER_BASE_URL", "https://your-hyper-instance.com")
    ```

## Error Handling

Common errors:

- `invalid_token`: Token is invalid or expired
- `connection_error`: Cannot reach Hyper service
- `timeout`: Request exceeded 30 second limit
