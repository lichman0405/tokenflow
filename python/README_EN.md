# OAuth Device Flow Library (Python)

[English](README_EN.md) | [中文](README_CN.md)

> ⚠️ **WARNING**: This library may violate GitHub Copilot's Terms of Service. Using this library to access GitHub Copilot without proper authorization may result in account suspension or termination. This project is for educational and research purposes only. Use at your own risk and ensure you have appropriate authorization before using this library.

## Overview

A Python implementation of OAuth2 device flow authentication, supporting GitHub Copilot and Hyper service integration.

## Features

- ✅ **Device Flow Authentication**: Implement OAuth2 device authorization flow
- ✅ **Token Lifecycle Management**: Automatic expiration detection and refresh
- ✅ **Multi-Service Support**: GitHub Copilot and Hyper service adapters
- ✅ **Disk Cache**: Read tokens from official GitHub Copilot client cache
- ✅ **Type Hints**: Full type annotation support
- ✅ **Error Handling**: Comprehensive error handling and retry mechanisms

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

### GitHub Copilot Authentication

```python
from oauth.copilot import request_device_code, poll_for_token, refresh_token_from_disk

# Try to read token from disk cache
github_token = refresh_token_from_disk()

if github_token:
    from oauth.copilot import refresh_token
    token = refresh_token(github_token)
else:
    # Start device flow
    device_code = request_device_code()
    print(f"Visit: {device_code.verification_uri}")
    print(f"Enter code: {device_code.user_code}")
    
    # Poll for token
    token = poll_for_token(device_code)

print(f"Access Token: {token.access_token}")
```

### Hyper Service Authentication

```python
from oauth.hyper import initiate_device_auth, poll_for_token, exchange_token

# Start device authorization
auth = initiate_device_auth()
print(f"Visit: {auth.verification_url}")
print(f"Enter code: {auth.user_code}")

# Poll for refresh token
refresh_token = poll_for_token(auth.device_code, auth.expires_in)

# Exchange for access token
token = exchange_token(refresh_token)

# Check if token is expired
if token.is_expired():
    token = exchange_token(refresh_token)
```

## Module Structure

```
oauth/
├── __init__.py          # Package initialization
├── token.py             # Token data structure and lifecycle management
├── copilot/             # GitHub Copilot integration
│   ├── __init__.py
│   ├── oauth.py         # Device flow implementation
│   ├── disk.py          # Disk cache reading
│   ├── client.py        # HTTP client with interceptor
│   ├── http.py          # HTTP headers
│   └── urls.py          # URL constants
└── hyper/               # Hyper service integration
    ├── __init__.py
    └── device.py        # Device flow implementation
```

## API Reference

### Token Management

```python
from oauth import Token

# Create token
token = Token(
    access_token="...",
    refresh_token="...",
    expires_in=3600
)

# Set expiration timestamp
token.set_expires_at()

# Check if expired (with 10% buffer)
if token.is_expired():
    # Refresh token
    pass

# Serialize to dict
data = token.to_dict()

# Deserialize from dict
token = Token.from_dict(data)
```

### Copilot Module

```python
from oauth.copilot import (
    request_device_code,
    poll_for_token,
    refresh_token,
    refresh_token_from_disk,
    create_client,
    NotAvailableError,
)

# Request device code
device_code = request_device_code(timeout=30)

# Poll for token (blocks until authorized or timeout)
token = poll_for_token(device_code, timeout=600)

# Refresh Copilot token
token = refresh_token(github_token)

# Read from disk cache
github_token = refresh_token_from_disk()

# Create HTTP client with X-Initiator header injection
client = create_client(is_sub_agent=False, debug=True)
```

### Hyper Module

```python
from oauth.hyper import (
    initiate_device_auth,
    poll_for_token,
    exchange_token,
    introspect_token,
)

# Initiate device authorization
auth = initiate_device_auth(timeout=30)

# Poll for refresh token
refresh_token = poll_for_token(auth.device_code, auth.expires_in)

# Exchange for access token
token = exchange_token(refresh_token, timeout=30)

# Introspect token (RFC 7662)
info = introspect_token(token.access_token)
if info.active:
    print(f"User ID: {info.sub}")
```

## Error Handling

```python
from oauth.copilot import NotAvailableError
import requests

try:
    token = poll_for_token(device_code)
except NotAvailableError:
    print("GitHub Copilot is not available for this account")
except TimeoutError:
    print("Authorization timed out")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

## Requirements

- Python 3.8+
- requests >= 2.31.0

## Author

- **Name**: Shibo Li
- **Email**: shadow.li981@gmail.com

## References

This project is inspired by and references:
- [charmbracelet/crush](https://github.com/charmbracelet/crush)

## License

MIT License
