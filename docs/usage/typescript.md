# TypeScript Usage Guide

Complete guide for using TokenFlow in TypeScript/JavaScript.

## Installation

```bash
npm install tokenflow
```

## GitHub Copilot

### Basic Device Flow

```typescript
import { copilot } from 'tokenflow';

async function main() {
    // Initiate device flow
    const deviceCode = await copilot.initiateDeviceFlow();
    
    console.log(`Visit: ${deviceCode.verificationUri}`);
    console.log(`Code: ${deviceCode.userCode}`);
    
    // Poll for token
    const token = await copilot.pollForToken(deviceCode);
    
    console.log(`Token: ${token.accessToken}`);
}

main().catch(console.error);
```

### With Success Callback

```typescript
const token = await copilot.pollForToken(
    deviceCode,
    (token) => {
        console.log("Authentication successful!");
        // Save token
        fs.writeFileSync("token.json", JSON.stringify(token));
    }
);
```

### Reading Cached Tokens

```typescript
import { copilot } from 'tokenflow';

try {
    const token = copilot.readTokenFromDisk();
    
    if (token.isExpired()) {
        console.log("Token expired");
    } else {
        console.log(`Valid token: ${token.accessToken}`);
    }
} catch (error) {
    console.log("No cached token found");
}
```

## Hyper Service

```typescript
import { hyper } from 'tokenflow';

async function main() {
    // Optional: Set custom base URL
    process.env.HYPER_BASE_URL = "https://custom.hyper.io";
    
    const deviceCode = await hyper.initiateDeviceFlow();
    
    console.log(`Visit: ${deviceCode.verificationUri}`);
    console.log(`Code: ${deviceCode.userCode}`);
    
    const token = await hyper.pollForToken(deviceCode);
    
    // Introspect token
    const info = await hyper.introspectToken(token.accessToken);
    
    console.log(`Active: ${info.active}`);
}

main().catch(console.error);
```

See [full usage examples](index.md) for more details.
