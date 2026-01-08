# Error Handling

Comprehensive error handling guide for TokenFlow.

## Common Errors

### OAuth Flow Errors

#### `authorization_pending`

User hasn't authorized the device code yet.

**Handling**: Continue polling (automatic in TokenFlow)

```python
# Handled automatically by poll_for_token
token = await poll_for_token(device_code)
```

---

#### `slow_down`

Polling too frequently.

**Handling**: Increase polling interval by 5 seconds (automatic)

=== "Go"
    ```go
    // Automatic handling in PollForToken
    if errorCode == "slow_down" {
        interval += 5 * time.Second
    }
    ```

=== "Python"
    ```python
    # Automatic handling in poll_for_token
    if error == "slow_down":
        interval += 5
    ```

---

#### `expired_token`

Device code has expired (typically 15 minutes).

**Handling**: Restart the flow

=== "Go"
    ```go
    deviceCode, err := copilot.InitiateDeviceFlow(ctx)
    if err != nil {
        if strings.Contains(err.Error(), "expired_token") {
            // Start new flow
            deviceCode, err = copilot.InitiateDeviceFlow(ctx)
        }
    }
    ```

=== "Python"
    ```python
    try:
        token = await poll_for_token(device_code)
    except Exception as e:
        if "expired_token" in str(e):
            device_code = await initiate_device_flow()
            token = await poll_for_token(device_code)
    ```

---

#### `access_denied`

User denied authorization.

**Handling**: Inform user and exit

```python
try:
    token = await poll_for_token(device_code)
except Exception as e:
    if "access_denied" in str(e):
        print("Authorization denied by user")
        sys.exit(1)
```

## Network Errors

### Timeout

All requests have 30-second timeout.

=== "Go"
    ```go
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    token, err := copilot.PollForToken(ctx, deviceCode, nil)
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            log.Println("Request timed out")
        }
    }
    ```

=== "Python"
    ```python
    try:
        token = await poll_for_token(device_code)
    except asyncio.TimeoutError:
        print("Request timed out")
    ```

=== "TypeScript"
    ```typescript
    try {
        const token = await pollForToken(deviceCode);
    } catch (error) {
        if (error.code === 'ETIMEDOUT') {
            console.log("Request timed out");
        }
    }
    ```

### Connection Error

Unable to reach the service.

=== "Go"
    ```go
    token, err := copilot.PollForToken(ctx, deviceCode, nil)
    if err != nil {
        if urlErr, ok := err.(*url.Error); ok {
            if urlErr.Timeout() {
                log.Println("Connection timeout")
            }
        }
    }
    ```

=== "Python"
    ```python
    import requests

    try:
        token = await poll_for_token(device_code)
    except requests.ConnectionError:
        print("Cannot connect to service")
    ```

## Token Errors

### Expired Token

Token has expired.

```python
token = load_token("token.json")
if token.is_expired():
    print("Token expired, re-authenticating...")
    token = await authenticate()
```

### Invalid Token

Token is malformed or corrupted.

=== "Go"
    ```go
    token, err := loadToken("token.json")
    if err != nil {
        if _, ok := err.(*json.SyntaxError); ok {
            log.Println("Corrupted token file")
            os.Remove("token.json")
            // Re-authenticate
        }
    }
    ```

=== "Python"
    ```python
    import json

    try:
        token = load_token("token.json")
    except json.JSONDecodeError:
        print("Corrupted token file")
        os.remove("token.json")
        # Re-authenticate
    ```

## File System Errors

### Token Not Found

No cached token available.

```python
try:
    token = load_token("token.json")
except FileNotFoundError:
    print("No cached token, starting authentication...")
    token = await authenticate()
```

### Permission Denied

Cannot write token file.

=== "Go"
    ```go
    err := saveToken(token, "token.json")
    if err != nil {
        if os.IsPermission(err) {
            log.Println("Permission denied: cannot write token file")
        }
    }
    ```

=== "Python"
    ```python
    try:
        save_token(token, "token.json")
    except PermissionError:
        print("Permission denied: cannot write token file")
    ```

## Best Practices

### 1. Always Handle Errors

Never ignore errors in production code:

```python
try:
    token = await poll_for_token(device_code)
except Exception as e:
    logger.error(f"Authentication failed: {e}")
    raise
```

### 2. Provide User Feedback

Inform users about what's happening:

```python
try:
    token = await poll_for_token(device_code)
except Exception as e:
    if "expired_token" in str(e):
        print("⚠️  Device code expired. Please try again.")
    elif "access_denied" in str(e):
        print("❌ Authorization denied")
    else:
        print(f"❌ Error: {e}")
```

### 3. Implement Retry Logic

For transient errors:

```python
for attempt in range(3):
    try:
        token = await poll_for_token(device_code)
        break
    except (ConnectionError, TimeoutError):
        if attempt == 2:
            raise
        await asyncio.sleep(2 ** attempt)
```

### 4. Log Errors

Keep audit trail:

```python
import logging

logger = logging.getLogger(__name__)

try:
    token = await poll_for_token(device_code)
except Exception as e:
    logger.exception("Authentication failed")
    raise
```

## Error Response Structure

OAuth error responses follow this structure:

```json
{
    "error": "authorization_pending",
    "error_description": "The authorization request is still pending",
    "error_uri": "https://docs.github.com/..."
}
```

Access fields in your error handler:

```python
if error_data.get("error") == "slow_down":
    # Increase interval
    pass
```
