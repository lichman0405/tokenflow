# Usage Guide

This document provides comprehensive usage examples for the OAuth Device Flow library across all supported languages.

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have proper authorization before using this library.

## Table of Contents

- [Go Usage](#go-usage)
- [Python Usage](#python-usage)
- [TypeScript Usage](#typescript-usage)
- [Common Patterns](#common-patterns)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)

---

## Go Usage

### Installation

```bash
cd go
go get github.com/user/oauth
```

### GitHub Copilot Authentication

#### Basic Device Flow

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/user/oauth/copilot"
)

func main() {
    ctx := context.Background()
    
    // Initiate device flow
    deviceCode, err := copilot.InitiateDeviceFlow(ctx)
    if err != nil {
        log.Fatalf("Failed to initiate device flow: %v", err)
    }
    
    // Display user code to the user
    fmt.Printf("Please visit: %s\n", deviceCode.VerificationURI)
    fmt.Printf("And enter code: %s\n", deviceCode.UserCode)
    
    // Poll for token
    token, err := copilot.PollForToken(ctx, deviceCode, nil)
    if err != nil {
        log.Fatalf("Failed to get token: %v", err)
    }
    
    fmt.Printf("Access Token: %s\n", token.AccessToken)
    fmt.Printf("Expires At: %s\n", token.ExpiresAt)
}
```

#### With Success Callback

```go
onSuccess := func(token *oauth.Token) {
    fmt.Println("Authentication successful!")
    // Save token to database or file
}

token, err := copilot.PollForToken(ctx, deviceCode, onSuccess)
```

#### Reading from Disk Cache

```go
package main

import (
    "fmt"
    "log"

    "github.com/user/oauth/copilot"
)

func main() {
    token, err := copilot.ReadTokenFromDisk()
    if err != nil {
        log.Fatalf("Failed to read token from disk: %v", err)
    }
    
    if token.IsExpired() {
        fmt.Println("Token is expired, need to refresh")
    } else {
        fmt.Printf("Valid token: %s\n", token.AccessToken)
    }
}
```

#### Using Custom HTTP Client

```go
package main

import (
    "context"
    "fmt"
    "net/http"

    "github.com/user/oauth/copilot"
)

func main() {
    ctx := context.Background()
    
    // Create custom HTTP client with X-Initiator header
    client := copilot.NewClient()
    
    // Use client for custom requests
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.github.com/copilot_internal/v2/token", nil)
    resp, err := client.Do(req)
    if err != nil {
        fmt.Printf("Request failed: %v\n", err)
        return
    }
    defer resp.Body.Close()
    
    fmt.Printf("Response status: %s\n", resp.Status)
}
```

### Hyper Authentication

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"

    "github.com/user/oauth/hyper"
)

func main() {
    ctx := context.Background()
    
    // Optional: Set custom base URL
    os.Setenv("HYPER_BASE_URL", "https://custom.hyper.io")
    
    // Initiate device flow
    deviceCode, err := hyper.InitiateDeviceFlow(ctx)
    if err != nil {
        log.Fatalf("Failed to initiate device flow: %v", err)
    }
    
    fmt.Printf("Visit: %s\n", deviceCode.VerificationURI)
    fmt.Printf("Code: %s\n", deviceCode.UserCode)
    
    // Poll for token with callback
    onSuccess := func(token *oauth.Token) {
        fmt.Println("Hyper authentication successful!")
    }
    
    token, err := hyper.PollForToken(ctx, deviceCode, onSuccess)
    if err != nil {
        log.Fatalf("Failed to get token: %v", err)
    }
    
    // Introspect token
    introspection, err := hyper.IntrospectToken(ctx, token.AccessToken)
    if err != nil {
        log.Fatalf("Failed to introspect token: %v", err)
    }
    
    fmt.Printf("Token active: %v\n", introspection.Active)
    fmt.Printf("Scope: %s\n", introspection.Scope)
}
```

---

## Python Usage

### Installation

```bash
cd python
pip install -r requirements.txt
# Or install the package
pip install -e .
```

### GitHub Copilot Authentication

#### Basic Device Flow

```python
import asyncio
from oauth.copilot import initiate_device_flow, poll_for_token

async def main():
    # Initiate device flow
    device_code = await initiate_device_flow()
    
    # Display to user
    print(f"Please visit: {device_code.verification_uri}")
    print(f"And enter code: {device_code.user_code}")
    
    # Poll for token
    token = await poll_for_token(device_code)
    
    print(f"Access Token: {token.access_token}")
    print(f"Expires At: {token.expires_at}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### With Success Callback

```python
def on_success(token):
    print("Authentication successful!")
    # Save token to file
    with open("token.json", "w") as f:
        f.write(token.to_json())

token = await poll_for_token(device_code, on_success=on_success)
```

#### Reading from Disk Cache

```python
from oauth.copilot import read_token_from_disk

try:
    token = read_token_from_disk()
    
    if token.is_expired():
        print("Token is expired")
    else:
        print(f"Valid token: {token.access_token}")
except FileNotFoundError:
    print("No cached token found")
```

#### Using Custom HTTP Client

```python
from oauth.copilot import Client

# Create client with X-Initiator header
client = Client()

# Make custom requests
response = client.get("https://api.github.com/copilot_internal/v2/token")
print(f"Status: {response.status_code}")
```

### Hyper Authentication

```python
import asyncio
import os
from oauth.hyper import initiate_device_flow, poll_for_token, introspect_token

async def main():
    # Optional: Set custom base URL
    os.environ["HYPER_BASE_URL"] = "https://custom.hyper.io"
    
    # Initiate device flow
    device_code = await initiate_device_flow()
    
    print(f"Visit: {device_code.verification_uri}")
    print(f"Code: {device_code.user_code}")
    
    # Poll for token
    def on_success(token):
        print("Hyper authentication successful!")
    
    token = await poll_for_token(device_code, on_success=on_success)
    
    # Introspect token
    introspection = await introspect_token(token.access_token)
    
    print(f"Token active: {introspection['active']}")
    print(f"Scope: {introspection.get('scope', '')}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Synchronous Usage

If you need synchronous code, you can use `asyncio.run()`:

```python
from oauth.copilot import initiate_device_flow, poll_for_token
import asyncio

def authenticate():
    device_code = asyncio.run(initiate_device_flow())
    token = asyncio.run(poll_for_token(device_code))
    return token

token = authenticate()
```

---

## TypeScript Usage

### Installation

```bash
cd ts
npm install
npm run build
```

### GitHub Copilot Authentication

#### Basic Device Flow

```typescript
import { copilot } from './src';

async function main() {
    // Initiate device flow
    const deviceCode = await copilot.initiateDeviceFlow();
    
    // Display to user
    console.log(`Please visit: ${deviceCode.verificationUri}`);
    console.log(`And enter code: ${deviceCode.userCode}`);
    
    // Poll for token
    const token = await copilot.pollForToken(deviceCode);
    
    console.log(`Access Token: ${token.accessToken}`);
    console.log(`Expires At: ${token.expiresAt}`);
}

main().catch(console.error);
```

#### With Success Callback

```typescript
const token = await copilot.pollForToken(
    deviceCode,
    (token) => {
        console.log("Authentication successful!");
        // Save token to file
        fs.writeFileSync("token.json", JSON.stringify(token));
    }
);
```

#### Reading from Disk Cache

```typescript
import { copilot } from './src';

try {
    const token = copilot.readTokenFromDisk();
    
    if (token.isExpired()) {
        console.log("Token is expired");
    } else {
        console.log(`Valid token: ${token.accessToken}`);
    }
} catch (error) {
    console.log("No cached token found");
}
```

#### Using Custom HTTP Client

```typescript
import { copilot } from './src';

// Create client with X-Initiator header
const client = copilot.createClient();

// Make custom requests
const response = await client.get(
    "https://api.github.com/copilot_internal/v2/token"
);
console.log(`Status: ${response.status}`);
```

### Hyper Authentication

```typescript
import { hyper } from './src';

async function main() {
    // Optional: Set custom base URL
    process.env.HYPER_BASE_URL = "https://custom.hyper.io";
    
    // Initiate device flow
    const deviceCode = await hyper.initiateDeviceFlow();
    
    console.log(`Visit: ${deviceCode.verificationUri}`);
    console.log(`Code: ${deviceCode.userCode}`);
    
    // Poll for token
    const token = await hyper.pollForToken(
        deviceCode,
        (token) => {
            console.log("Hyper authentication successful!");
        }
    );
    
    // Introspect token
    const introspection = await hyper.introspectToken(token.accessToken);
    
    console.log(`Token active: ${introspection.active}`);
    console.log(`Scope: ${introspection.scope || ''}`);
}

main().catch(console.error);
```

---

## Common Patterns

### Token Persistence

#### Go

```go
import (
    "encoding/json"
    "os"
)

// Save token
func saveToken(token *oauth.Token, filename string) error {
    data, err := json.Marshal(token)
    if err != nil {
        return err
    }
    return os.WriteFile(filename, data, 0600)
}

// Load token
func loadToken(filename string) (*oauth.Token, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        return nil, err
    }
    var token oauth.Token
    err = json.Unmarshal(data, &token)
    return &token, err
}
```

#### Python

```python
import json
from oauth.token import Token

# Save token
def save_token(token: Token, filename: str):
    with open(filename, "w") as f:
        f.write(token.to_json())

# Load token
def load_token(filename: str) -> Token:
    with open(filename, "r") as f:
        data = json.load(f)
    return Token.from_dict(data)
```

#### TypeScript

```typescript
import fs from 'fs';
import { Token } from './token';

// Save token
function saveToken(token: Token, filename: string): void {
    fs.writeFileSync(filename, JSON.stringify(token), { mode: 0o600 });
}

// Load token
function loadToken(filename: string): Token {
    const data = JSON.parse(fs.readFileSync(filename, 'utf-8'));
    return Token.fromJSON(data);
}
```

### Token Refresh Logic

```typescript
async function getValidToken(): Promise<Token> {
    let token = loadToken("token.json");
    
    // Check if token needs refresh (within 10% of expiration)
    if (token.isExpired()) {
        // Re-authenticate
        const deviceCode = await copilot.initiateDeviceFlow();
        console.log(`Visit: ${deviceCode.verificationUri}`);
        console.log(`Code: ${deviceCode.userCode}`);
        token = await copilot.pollForToken(deviceCode);
        saveToken(token, "token.json");
    }
    
    return token;
}
```

### Timeout Handling

All implementations have built-in 30-second timeouts. To customize:

#### Go

```go
ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
defer cancel()

token, err := copilot.PollForToken(ctx, deviceCode, nil)
```

#### Python

```python
# The implementation uses a 30-second timeout internally
# For custom timeout, modify the http.py request calls
```

#### TypeScript

```typescript
// The implementation uses a 30-second timeout internally
// Axios allows custom timeout in client configuration
```

---

## Error Handling

### Common Errors

#### Authorization Pending

When polling for token, you may receive "authorization_pending" - this is normal and the library will retry automatically.

#### Slow Down

If polling too frequently, you'll receive "slow_down". The library automatically increases the interval by 5 seconds.

#### Expired Token

```python
# Python example
if token.is_expired():
    print("Token expired, need to re-authenticate")
```

#### Network Errors

All implementations include:
- Connection timeouts (30 seconds)
- Response size limits (1MB)
- Retry logic for transient failures

### Example Error Handling

#### Go

```go
token, err := copilot.PollForToken(ctx, deviceCode, nil)
if err != nil {
    if errors.Is(err, context.DeadlineExceeded) {
        log.Println("Timeout waiting for user authorization")
    } else {
        log.Printf("Authentication failed: %v", err)
    }
    return
}
```

#### Python

```python
try:
    token = await poll_for_token(device_code)
except asyncio.TimeoutError:
    print("Timeout waiting for user authorization")
except Exception as e:
    print(f"Authentication failed: {e}")
```

#### TypeScript

```typescript
try {
    const token = await copilot.pollForToken(deviceCode);
} catch (error) {
    if (error.code === 'ETIMEDOUT') {
        console.log("Timeout waiting for user authorization");
    } else {
        console.error(`Authentication failed: ${error.message}`);
    }
}
```

---

## Security Considerations

### 1. Token Storage

- Always store tokens with restricted permissions (0600 on Unix)
- Never commit tokens to version control
- Use encrypted storage for production systems

### 2. Response Size Limits

All implementations limit response sizes to 1MB to prevent memory exhaustion:

```python
# Python example - automatically enforced
MAX_RESPONSE_SIZE = 1024 * 1024  # 1MB
```

### 3. Timeouts

All HTTP requests have 30-second timeouts to prevent hanging connections.

### 4. Token Expiration Buffer

Tokens are considered expired 10% before actual expiration to prevent race conditions:

```python
# Python example
def is_expired(self) -> bool:
    buffer = self.expires_in * 0.1
    return datetime.now() >= (self.expires_at - timedelta(seconds=buffer))
```

### 5. Environment Variables

For Hyper service, base URL can be configured via environment variable:

```bash
export HYPER_BASE_URL="https://custom.hyper.io"
```

### 6. HTTPS Only

All implementations enforce HTTPS for API calls (except local testing).

---

## Advanced Usage

### Custom Polling Intervals

The device flow uses intervals specified by the OAuth server. To modify:

#### Go

```go
// The interval is returned in deviceCode.Interval
// Default minimum is 5 seconds
```

#### Python

```python
# Customize in poll_for_token function
interval = device_code.interval  # Use server-specified interval
```

### Integration with CLI Tools

Example CLI tool structure:

```go
package main

import (
    "context"
    "flag"
    "fmt"
    "log"
    "os"

    "github.com/user/oauth/copilot"
)

func main() {
    tokenFile := flag.String("token", "token.json", "Token file path")
    flag.Parse()

    // Try to load existing token
    token, err := loadToken(*tokenFile)
    if err != nil || token.IsExpired() {
        // Need fresh authentication
        token, err = authenticate()
        if err != nil {
            log.Fatal(err)
        }
        saveToken(token, *tokenFile)
    }

    fmt.Printf("Valid token: %s\n", token.AccessToken)
}

func authenticate() (*oauth.Token, error) {
    ctx := context.Background()
    
    deviceCode, err := copilot.InitiateDeviceFlow(ctx)
    if err != nil {
        return nil, err
    }
    
    fmt.Fprintf(os.Stderr, "Visit: %s\n", deviceCode.VerificationURI)
    fmt.Fprintf(os.Stderr, "Code: %s\n", deviceCode.UserCode)
    
    return copilot.PollForToken(ctx, deviceCode, nil)
}
```

---

## Troubleshooting

### Issue: "No cached token found"

**Solution**: Run the device flow authentication to obtain a token first.

### Issue: "Token expired"

**Solution**: Re-authenticate using the device flow.

### Issue: "Connection timeout"

**Solution**: Check network connectivity and firewall settings. Ensure you can reach GitHub/Hyper APIs.

### Issue: "Invalid response size"

**Solution**: Response exceeded 1MB limit. This indicates a potential server issue or attack.

### Issue: "User didn't authorize in time"

**Solution**: The device code expires (typically after 15 minutes). Start a new device flow.

---

## Contributing

When contributing to this project, please ensure:

1. All three language implementations remain synchronized
2. Security measures (timeouts, size limits) are maintained
3. Documentation is updated in both English and Chinese
4. Tests are added for new features

---

## License

MIT License - See individual language implementations for details.

---

## Author

**Shibo Li** - shadow.li981@gmail.com

## Reference

This project is inspired by [charmbracelet/crush](https://github.com/charmbracelet/crush).

---

**Last Updated**: 2026-01-08
