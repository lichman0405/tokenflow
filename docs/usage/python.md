# Python Usage Guide

Complete guide for using TokenFlow in Python.

## Installation

```bash
pip install tokenflow
```

## GitHub Copilot

### Basic Device Flow

```python
import asyncio
from oauth.copilot import initiate_device_flow, poll_for_token

async def main():
    # Initiate device flow
    device_code = await initiate_device_flow()
    
    print(f"Visit: {device_code.verification_uri}")
    print(f"Code: {device_code.user_code}")
    
    # Poll for token
    token = await poll_for_token(device_code)
    
    print(f"Token: {token.access_token}")

if __name__ == "__main__":
    asyncio.run(main())
```

### With Success Callback

```python
def on_success(token):
    print("Authentication successful!")
    # Save token
    with open("token.json", "w") as f:
        f.write(token.to_json())

token = await poll_for_token(device_code, on_success=on_success)
```

### Reading Cached Tokens

```python
from oauth.copilot import read_token_from_disk

try:
    token = read_token_from_disk()
    
    if token.is_expired():
        print("Token expired")
    else:
        print(f"Valid token: {token.access_token}")
except FileNotFoundError:
    print("No cached token found")
```

## Hyper Service

```python
import asyncio
import os
from oauth.hyper import initiate_device_flow, poll_for_token, introspect_token

async def main():
    # Optional: Set custom base URL
    os.environ["HYPER_BASE_URL"] = "https://custom.hyper.io"
    
    device_code = await initiate_device_flow()
    
    print(f"Visit: {device_code.verification_uri}")
    print(f"Code: {device_code.user_code}")
    
    token = await poll_for_token(device_code)
    
    # Introspect token
    info = await introspect_token(token.access_token)
    
    print(f"Active: {info['active']}")

if __name__ == "__main__":
    asyncio.run(main())
```

See [full usage examples](index.md) for more details.
