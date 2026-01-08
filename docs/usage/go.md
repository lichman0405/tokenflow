# Go Usage Guide

Complete guide for using TokenFlow in Go.

## Installation

```bash
go get github.com/lichman0405/tokenflow/go
```

## GitHub Copilot

### Basic Device Flow

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/lichman0405/tokenflow/go/copilot"
)

func main() {
    ctx := context.Background()
    
    // Initiate device flow
    deviceCode, err := copilot.InitiateDeviceFlow(ctx)
    if err != nil {
        log.Fatalf("Failed to initiate: %v", err)
    }
    
    fmt.Printf("Visit: %s\n", deviceCode.VerificationURI)
    fmt.Printf("Code: %s\n", deviceCode.UserCode)
    
    // Poll for token
    token, err := copilot.PollForToken(ctx, deviceCode, nil)
    if err != nil {
        log.Fatalf("Failed to get token: %v", err)
    }
    
    fmt.Printf("Token: %s\n", token.AccessToken)
}
```

### With Success Callback

```go
onSuccess := func(token *oauth.Token) {
    fmt.Println("Authentication successful!")
    // Save token or trigger other actions
}

token, err := copilot.PollForToken(ctx, deviceCode, onSuccess)
```

### Reading Cached Tokens

```go
token, err := copilot.ReadTokenFromDisk()
if err != nil {
    log.Printf("No cached token: %v", err)
    // Initiate new flow
} else if token.IsExpired() {
    fmt.Println("Token expired, need refresh")
} else {
    fmt.Printf("Valid token: %s\n", token.AccessToken)
}
```

## Hyper Service

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/lichman0405/tokenflow/go/hyper"
)

func main() {
    ctx := context.Background()
    
    // Optional: Set custom base URL
    os.Setenv("HYPER_BASE_URL", "https://custom.hyper.io")
    
    deviceCode, err := hyper.InitiateDeviceFlow(ctx)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Visit: %s\n", deviceCode.VerificationURI)
    fmt.Printf("Code: %s\n", deviceCode.UserCode)
    
    token, err := hyper.PollForToken(ctx, deviceCode, nil)
    if err != nil {
        log.Fatal(err)
    }
    
    // Introspect token
    info, err := hyper.IntrospectToken(ctx, token.AccessToken)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Active: %v\n", info.Active)
}
```

See [full usage examples](index.md) for more details.
