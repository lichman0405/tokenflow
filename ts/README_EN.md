# OAuth Device Flow Library (TypeScript)

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

## Overview

A TypeScript implementation of OAuth2 device flow authentication, supporting GitHub Copilot and Hyper service integration.

## Features

- ✅ **Device Flow Authentication**: Implement OAuth2 device authorization flow
- ✅ **Token Lifecycle Management**: Automatic expiration detection and refresh
- ✅ **Multi-Service Support**: GitHub Copilot and Hyper service adapters
- ✅ **Disk Cache**: Read tokens from official GitHub Copilot client cache
- ✅ **Type Safety**: Full TypeScript type definitions
- ✅ **Error Handling**: Comprehensive error handling and retry mechanisms
- ✅ **Async/Await**: Modern async programming support

## Installation

```bash
npm install
```

## Build

```bash
npm run build
```

## Quick Start

### GitHub Copilot Authentication

```typescript
import { copilot, Token } from "oauth-deviceflow";

async function authenticate() {
  // Try to read token from disk cache
  const githubToken = copilot.refreshTokenFromDisk();

  let token: Token;
  if (githubToken) {
    token = await copilot.refreshToken(githubToken);
  } else {
    // Start device flow
    const deviceCode = await copilot.requestDeviceCode();
    console.log(`Visit: ${deviceCode.verificationUri}`);
    console.log(`Enter code: ${deviceCode.userCode}`);
    
    // Poll for token
    token = await copilot.pollForToken(deviceCode);
  }

  console.log(`Access Token: ${token.accessToken}`);
}

authenticate().catch(console.error);
```

### Hyper Service Authentication

```typescript
import { hyper, Token } from "oauth-deviceflow";

async function authenticate() {
  // Start device authorization
  const auth = await hyper.initiateDeviceAuth();
  console.log(`Visit: ${auth.verificationUrl}`);
  console.log(`Enter code: ${auth.userCode}`);

  // Poll for refresh token
  const refreshToken = await hyper.pollForToken(auth.deviceCode, auth.expiresIn);

  // Exchange for access token
  let token = await hyper.exchangeToken(refreshToken);

  // Check if token is expired
  if (token.isExpired()) {
    token = await hyper.exchangeToken(refreshToken);
  }

  console.log(`Access Token: ${token.accessToken}`);
}

authenticate().catch(console.error);
```

## Module Structure

```
src/
├── index.ts             # Package entry point
├── token.ts             # Token data structure and lifecycle management
├── copilot/             # GitHub Copilot integration
│   ├── index.ts
│   ├── oauth.ts         # Device flow implementation
│   ├── disk.ts          # Disk cache reading
│   ├── client.ts        # HTTP client with interceptor
│   ├── http.ts          # HTTP headers
│   └── urls.ts          # URL constants
└── hyper/               # Hyper service integration
    ├── index.ts
    └── device.ts        # Device flow implementation
```

## API Reference

### Token Management

```typescript
import { Token } from "oauth-deviceflow";

// Create token
const token = new Token(
  "access_token_here",
  "refresh_token_here",
  3600,
  0
);

// Set expiration timestamp
token.setExpiresAt();

// Check if expired (with 10% buffer)
if (token.isExpired()) {
  // Refresh token
}

// Serialize to JSON
const data = token.toJSON();

// Deserialize from JSON
const token2 = Token.fromJSON(data);
```

### Copilot Module

```typescript
import { copilot } from "oauth-deviceflow";

// Request device code
const deviceCode = await copilot.requestDeviceCode(30000);

// Poll for token (blocks until authorized or timeout)
const token = await copilot.pollForToken(deviceCode, 600000);

// Refresh Copilot token
const newToken = await copilot.refreshToken(githubToken);

// Read from disk cache
const githubToken = copilot.refreshTokenFromDisk();

// Create HTTP client with X-Initiator header injection
const client = copilot.createClient(false, true);
```

### Hyper Module

```typescript
import { hyper } from "oauth-deviceflow";

// Initiate device authorization
const auth = await hyper.initiateDeviceAuth(30000);

// Poll for refresh token
const refreshToken = await hyper.pollForToken(auth.deviceCode, auth.expiresIn);

// Exchange for access token
const token = await hyper.exchangeToken(refreshToken, 30000);

// Introspect token (RFC 7662)
const info = await hyper.introspectToken(token.accessToken);
if (info.active) {
  console.log(`User ID: ${info.sub}`);
}
```

## Error Handling

```typescript
import { copilot } from "oauth-deviceflow";

try {
  const token = await copilot.pollForToken(deviceCode);
} catch (error) {
  if (error instanceof copilot.NotAvailableError) {
    console.error("GitHub Copilot is not available for this account");
  } else if (error.message === "Authorization timed out") {
    console.error("Authorization timed out");
  } else {
    console.error("Network error:", error);
  }
}
```

## Requirements

- Node.js 16+
- TypeScript 5.3+
- axios >= 1.6.0

## Author

- **Name**: Shibo Li
- **Email**: shadow.li981@gmail.com

## References

This project is inspired by and references:
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## License

MIT License
