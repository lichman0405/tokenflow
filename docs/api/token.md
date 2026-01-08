# Token Management

Core token structure and lifecycle management across all implementations.

## Token Structure

All implementations use a unified token structure with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | The OAuth access token |
| `token_type` | string | Token type (usually "Bearer") |
| `expires_in` | int | Token lifetime in seconds |
| `refresh_token` | string | Optional refresh token |
| `scope` | string | Token scope |
| `expires_at` | datetime/timestamp | Calculated expiration timestamp |

## Token Lifecycle

### 1. Creation

Tokens are created after successful OAuth flow:

=== "Go"
    ```go
    token := &Token{
        AccessToken:  response.AccessToken,
        TokenType:    response.TokenType,
        ExpiresIn:    response.ExpiresIn,
        RefreshToken: response.RefreshToken,
        Scope:        response.Scope,
    }
    token.CalculateExpiry()
    ```

=== "Python"
    ```python
    token = Token(
        access_token=response["access_token"],
        token_type=response["token_type"],
        expires_in=response["expires_in"],
        refresh_token=response.get("refresh_token"),
        scope=response.get("scope", "")
    )
    ```

=== "TypeScript"
    ```typescript
    const token = new Token({
        accessToken: response.access_token,
        tokenType: response.token_type,
        expiresIn: response.expires_in,
        refreshToken: response.refresh_token,
        scope: response.scope
    });
    ```

### 2. Expiration Check

All implementations include a **10% buffer** before actual expiration:

```python
def is_expired(self) -> bool:
    buffer = self.expires_in * 0.1
    return datetime.now() >= (self.expires_at - timedelta(seconds=buffer))
```

This prevents race conditions where the token expires during a request.

### 3. Serialization

Tokens can be serialized to JSON for storage:

=== "Go"
    ```go
    data, err := json.Marshal(token)
    ```

=== "Python"
    ```python
    json_str = token.to_json()
    ```

=== "TypeScript"
    ```typescript
    const json = JSON.stringify(token);
    ```

## Best Practices

### Secure Storage

!!! warning "Security"
    Always store tokens securely with restricted permissions (0600 on Unix).

=== "Go"
    ```go
    err := os.WriteFile("token.json", data, 0600)
    ```

=== "Python"
    ```python
    with open("token.json", "w") as f:
        os.chmod("token.json", 0o600)
        f.write(token.to_json())
    ```

=== "TypeScript"
    ```typescript
    fs.writeFileSync("token.json", JSON.stringify(token), { mode: 0o600 });
    ```

### Token Refresh

Check expiration before each use:

```python
if token.is_expired():
    # Re-authenticate or refresh
    token = await initiate_device_flow()
```

### Error Handling

Handle token-related errors gracefully:

- `FileNotFoundError` / `ENOENT`: No cached token
- `JSONDecodeError`: Corrupted token file
- `Expired`: Token needs refresh
