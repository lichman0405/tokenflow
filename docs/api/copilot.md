# GitHub Copilot API

OAuth2 Device Flow implementation for GitHub Copilot.

## Functions

### `InitiateDeviceFlow` / `initiate_device_flow`

Initiates the OAuth device authorization flow.

**Returns**: Device code response containing:
- `device_code`: Device verification code
- `user_code`: User-friendly code to display
- `verification_uri`: URL for user authorization
- `expires_in`: Code expiration time (seconds)
- `interval`: Polling interval (seconds)

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

**Example**:

=== "Go"
    ```go
    ctx := context.Background()
    deviceCode, err := copilot.InitiateDeviceFlow(ctx)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Visit: %s\n", deviceCode.VerificationURI)
    fmt.Printf("Code: %s\n", deviceCode.UserCode)
    ```

=== "Python"
    ```python
    device_code = await initiate_device_flow()
    print(f"Visit: {device_code.verification_uri}")
    print(f"Code: {device_code.user_code}")
    ```

=== "TypeScript"
    ```typescript
    const deviceCode = await initiateDeviceFlow();
    console.log(`Visit: ${deviceCode.verificationUri}`);
    console.log(`Code: ${deviceCode.userCode}`);
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

**Behavior**:
- Polls every `interval` seconds
- Handles `authorization_pending` automatically
- Increases interval by 5s on `slow_down` error
- Calls `on_success` callback when complete

---

### `ReadTokenFromDisk` / `read_token_from_disk`

Reads cached token from official Copilot client.

**Returns**: Cached token if available

=== "Go"
    ```go
    func ReadTokenFromDisk() (*Token, error)
    ```

=== "Python"
    ```python
    def read_token_from_disk() -> Token
    ```

=== "TypeScript"
    ```typescript
    function readTokenFromDisk(): Token
    ```

**Cache Locations**:
- **macOS**: `~/Library/Application Support/github-copilot/hosts.json`
- **Linux**: `~/.config/github-copilot/hosts.json`
- **Windows**: `%APPDATA%\github-copilot\hosts.json`

---

### `NewClient` / `Client`

Creates HTTP client with X-Initiator header injection.

=== "Go"
    ```go
    func NewClient() *http.Client
    ```

=== "Python"
    ```python
    client = Client()
    response = client.get("https://api.github.com/...")
    ```

=== "TypeScript"
    ```typescript
    const client = createClient();
    const response = await client.get("https://api.github.com/...");
    ```

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `ClientID` | `Iv1.b507a08c87ecfe98` | GitHub Copilot client ID |
| `DeviceCodeURL` | `https://github.com/login/device/code` | Device code endpoint |
| `AccessTokenURL` | `https://github.com/login/oauth/access_token` | Token exchange endpoint |

## Error Handling

Common errors:

- `authorization_pending`: User hasn't authorized yet (retry)
- `slow_down`: Polling too fast (increase interval)
- `expired_token`: Device code expired (restart flow)
- `access_denied`: User denied authorization
