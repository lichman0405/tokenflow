# OAuth Library for Go

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

OAuth2 Device Flow implementation for GitHub Copilot and Hyper services.

## Installation

```bash
go get github.com/user/oauth
```

## Features

### Token Management

The `oauth.Token` struct provides unified token management:
- Automatic expiration calculation
- 10% buffer for token refresh (refreshes before actual expiration)
- JSON serialization support

```go
import "github.com/user/oauth"

token := &oauth.Token{
    AccessToken:  "...",
    RefreshToken: "...",
    ExpiresIn:    3600,
}
token.SetExpiresAt()

if token.IsExpired() {
    // Refresh the token
}
```

### GitHub Copilot

Device flow authentication for GitHub Copilot:

```go
import (
    "context"
    "github.com/user/oauth/copilot"
)

ctx := context.Background()

// Step 1: Request device code
dc, err := copilot.RequestDeviceCode(ctx)
if err != nil {
    log.Fatal(err)
}

// Display to user
fmt.Printf("Go to %s and enter code: %s\n", dc.VerificationURI, dc.UserCode)

// Step 2: Poll for token
token, err := copilot.PollForToken(ctx, dc)
if err != nil {
    log.Fatal(err)
}

// Step 3: Refresh when expired
if token.IsExpired() {
    token, err = copilot.RefreshToken(ctx, token.RefreshToken)
}
```

#### Disk Cache

Read cached tokens from official GitHub Copilot client:

```go
if refreshToken, ok := copilot.RefreshTokenFromDisk(); ok {
    token, err := copilot.RefreshToken(ctx, refreshToken)
    // Use token...
}
```

#### Custom HTTP Client

Create an HTTP client with X-Initiator header injection:

```go
client := copilot.NewClient(false) // isSubAgent = false

// The client automatically sets X-Initiator header based on request body
```

### Hyper Service

Device flow authentication for Hyper:

```go
import (
    "context"
    "github.com/user/oauth/hyper"
)

ctx := context.Background()

// Step 1: Initiate device auth
auth, err := hyper.InitiateDeviceAuth(ctx)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Go to %s and enter code: %s\n", auth.VerificationURL, auth.UserCode)

// Step 2: Poll for token
refreshToken, err := hyper.PollForToken(ctx, auth.DeviceCode, auth.ExpiresIn, func(userID string) {
    // Optional: called on success with user ID
    fmt.Printf("Authenticated as user: %s\n", userID)
})
if err != nil {
    log.Fatal(err)
}

// Step 3: Exchange for access token
token, err := hyper.ExchangeToken(ctx, refreshToken)
if err != nil {
    log.Fatal(err)
}

// Step 4: Introspect token (optional)
info, err := hyper.IntrospectToken(ctx, token.AccessToken)
if info.Active {
    fmt.Printf("Token valid until: %d\n", info.Exp)
}
```

#### Configuration

Set the Hyper base URL via environment variable:

```bash
export HYPER_BASE_URL=https://api.hyper.example.com
```

## Project Structure

```
go/
├── go.mod              # Module definition
├── token.go            # Token struct and methods
├── copilot/
│   ├── oauth.go        # Device flow for Copilot
│   ├── client.go       # Custom HTTP client
│   ├── disk.go         # Disk cache reading
│   ├── http.go         # HTTP headers
│   └── urls.go         # URL constants
└── hyper/
    └── device.go       # Device flow for Hyper
```

## Security

- All HTTP requests have 30-second timeouts
- Response body size limited to 1MB to prevent memory exhaustion
- Tokens are refreshed before actual expiration (10% buffer)

## Author

- **Name**: Shibo Li
- **Email**: shadow.li981@gmail.com

## References

This project is inspired by and references:
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## License

MIT License
