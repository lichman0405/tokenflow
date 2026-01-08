# Security Considerations

TokenFlow implements multiple security measures to protect your authentication flow.

## Built-in Security Features

### 1. Request Timeouts

All HTTP requests have a **30-second timeout** to prevent hanging connections:

- Prevents indefinite waiting on network issues
- Protects against slow loris attacks
- Ensures responsive error handling

### 2. Response Size Limits

Responses are limited to **1MB** to prevent memory exhaustion:

=== "Go"
    ```go
    const maxResponseSize = 1024 * 1024 // 1MB
    ```

=== "Python"
    ```python
    MAX_RESPONSE_SIZE = 1024 * 1024  # 1MB
    ```

=== "TypeScript"
    ```typescript
    const MAX_RESPONSE_SIZE = 1024 * 1024; // 1MB
    ```

### 3. Token Expiration Buffer

Tokens are refreshed **10% before actual expiration** to prevent race conditions:

```python
def is_expired(self) -> bool:
    buffer = self.expires_in * 0.1
    return datetime.now() >= (self.expires_at - timedelta(seconds=buffer))
```

### 4. HTTPS Enforcement

All API calls use HTTPS to ensure encrypted communication.

## Best Practices

### Token Storage

!!! warning "Secure Token Storage"
    Always store tokens with restricted permissions:
    
    - **Unix/Linux/macOS**: `chmod 600 token.json`
    - **Windows**: Set appropriate ACLs
    - Never commit tokens to version control

### Environment Variables

For Hyper service configuration:

```bash
export HYPER_BASE_URL="https://your-hyper-instance.com"
```

### Production Deployment

1. **Use encrypted storage** for tokens
2. **Rotate tokens regularly**
3. **Monitor for unauthorized access**
4. **Implement rate limiting**
5. **Log authentication attempts**

## Compliance

!!! warning "GitHub Copilot Terms of Service"
    Using TokenFlow to access GitHub Copilot may violate GitHub's Terms of Service. This project is intended for:
    
    - Educational purposes
    - Research and development
    - Understanding OAuth2 device flow
    
    **Always obtain proper authorization before use.**

## Reporting Security Issues

If you discover a security vulnerability, please email:

📧 [shadow.li981@gmail.com](mailto:shadow.li981@gmail.com)

**Do not** open a public issue for security vulnerabilities.
