# Quick Start

Get started with TokenFlow in just a few minutes!

## Choose Your Language

=== "Go"

    ### Basic Usage

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
            log.Fatal(err)
        }
        
        // Show user code
        fmt.Printf("Visit: %s\n", deviceCode.VerificationURI)
        fmt.Printf("Code: %s\n", deviceCode.UserCode)
        
        // Poll for token
        token, err := copilot.PollForToken(ctx, deviceCode, nil)
        if err != nil {
            log.Fatal(err)
        }
        
        fmt.Printf("Access Token: %s\n", token.AccessToken)
    }
    ```

    [Full Go Documentation →](../usage/go.md)

=== "Python"

    ### Basic Usage

    ```python
    import asyncio
    from oauth.copilot import initiate_device_flow, poll_for_token

    async def main():
        # Initiate device flow
        device_code = await initiate_device_flow()
        
        # Show user code
        print(f"Visit: {device_code.verification_uri}")
        print(f"Code: {device_code.user_code}")
        
        # Poll for token
        token = await poll_for_token(device_code)
        
        print(f"Access Token: {token.access_token}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

    [Full Python Documentation →](../usage/python.md)

=== "TypeScript"

    ### Basic Usage

    ```typescript
    import { copilot } from 'tokenflow';

    async function main() {
        // Initiate device flow
        const deviceCode = await copilot.initiateDeviceFlow();
        
        // Show user code
        console.log(`Visit: ${deviceCode.verificationUri}`);
        console.log(`Code: ${deviceCode.userCode}`);
        
        // Poll for token
        const token = await copilot.pollForToken(deviceCode);
        
        console.log(`Access Token: ${token.accessToken}`);
    }

    main().catch(console.error);
    ```

    [Full TypeScript Documentation →](../usage/typescript.md)

## What's Next?

- 📖 [Read the complete Usage Guide](../usage/index.md)
- 🔍 [Explore API Reference](../api/token.md)
- 🏗️ [Learn about the Architecture](../design/architecture.md)
