"""
Hyper device flow authentication implementation.

Implements OAuth2 device flow for Hyper service including
device authorization, token exchange, and token introspection.
"""

from dataclasses import dataclass
from typing import Optional, Callable
import json
import os
import time
import socket
import requests

from ..token import Token


# Maximum response size (1MB) to prevent memory exhaustion
MAX_RESPONSE_SIZE = 1024 * 1024


# Base URL - configured via environment variable or default
def get_base_url() -> str:
    """Get the base URL for Hyper API."""
    return os.getenv("HYPER_BASE_URL", "https://api.hyper.example.com")


@dataclass
class DeviceAuthResponse:
    """
    Device authorization response.
    
    Attributes:
        device_code: Code used for polling
        user_code: Code displayed to the user
        verification_url: URL where user authorizes the device
        expires_in: Seconds until the device code expires
    """
    device_code: str
    user_code: str
    verification_url: str
    expires_in: int

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceAuthResponse":
        """Create from API response."""
        return cls(
            device_code=data["device_code"],
            user_code=data["user_code"],
            verification_url=data["verification_url"],
            expires_in=data["expires_in"],
        )


@dataclass
class TokenResponse:
    """
    Token polling response.
    
    Attributes:
        refresh_token: Refresh token for obtaining access tokens
        user_id: User identifier
        organization_id: Organization identifier
        organization_name: Organization name
        error: Error code if request failed
        error_description: Human-readable error description
    """
    refresh_token: str = ""
    user_id: str = ""
    organization_id: str = ""
    organization_name: str = ""
    error: str = ""
    error_description: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "TokenResponse":
        """Create from API response."""
        return cls(
            refresh_token=data.get("refresh_token", ""),
            user_id=data.get("user_id", ""),
            organization_id=data.get("organization_id", ""),
            organization_name=data.get("organization_name", ""),
            error=data.get("error", ""),
            error_description=data.get("error_description", ""),
        )


@dataclass
class IntrospectTokenResponse:
    """
    Token introspection response (RFC 7662).
    
    Attributes:
        active: Whether the token is active
        sub: Subject (user ID)
        org_id: Organization ID
        exp: Expiration timestamp
        iat: Issued at timestamp
        iss: Issuer
        jti: JWT ID
    """
    active: bool
    sub: str = ""
    org_id: str = ""
    exp: int = 0
    iat: int = 0
    iss: str = ""
    jti: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "IntrospectTokenResponse":
        """Create from API response."""
        return cls(
            active=data.get("active", False),
            sub=data.get("sub", ""),
            org_id=data.get("org_id", ""),
            exp=data.get("exp", 0),
            iat=data.get("iat", 0),
            iss=data.get("iss", ""),
            jti=data.get("jti", ""),
        )


def _get_device_name() -> str:
    """
    Get a descriptive device name.
    
    Returns:
        Device name including hostname if available
    """
    try:
        hostname = socket.gethostname()
        if hostname:
            return f"Crush ({hostname})"
    except Exception:
        pass
    return "Crush"


def initiate_device_auth(timeout: int = 30) -> DeviceAuthResponse:
    """
    Initiate the device authorization flow.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        DeviceAuthResponse containing user_code and verification_url
        
    Raises:
        requests.RequestException: If the request fails
    """
    url = f"{get_base_url()}/device/auth"
    
    payload = {
        "device_name": _get_device_name()
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "crush",
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    
    return DeviceAuthResponse.from_dict(response.json())


def poll_for_token(
    device_code: str, 
    expires_in: int,
    on_success: Optional[Callable[[str], None]] = None
) -> str:
    """
    Poll for authorization completion and get refresh token.
    
    Args:
        device_code: Device code from initiate_device_auth()
        expires_in: Time in seconds until device code expires
        on_success: Optional callback with user_id when authorization succeeds.
                    This matches Go's event.Alias() behavior for user tracking.
        
    Returns:
        Refresh token
        
    Raises:
        TimeoutError: If authorization times out
        Exception: If authorization fails
        requests.RequestException: If the request fails
    """
    deadline = time.time() + expires_in
    interval = 5  # Poll every 5 seconds
    
    while time.time() < deadline:
        response = _poll_once(device_code)
        
        if response.refresh_token:
            # Call on_success callback if provided (matches Go's event.Alias)
            if on_success and response.user_id:
                on_success(response.user_id)
            return response.refresh_token
        
        if response.error == "authorization_pending":
            time.sleep(interval)
            continue
        
        if response.error:
            raise Exception(response.error_description or response.error)
    
    raise TimeoutError("Authorization timed out")


def _poll_once(device_code: str) -> TokenResponse:
    """
    Perform a single polling request.
    
    Args:
        device_code: Device code
        
    Returns:
        TokenResponse
        
    Raises:
        requests.RequestException: If the request fails
    """
    url = f"{get_base_url()}/device/auth/{device_code}"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "crush",
    }
    
    response = requests.get(
        url,
        headers=headers,
        timeout=30,
        stream=True,  # Enable streaming to limit response size
    )
    
    # Read with size limit to prevent memory exhaustion
    content = response.raw.read(MAX_RESPONSE_SIZE + 1)
    if len(content) > MAX_RESPONSE_SIZE:
        raise ValueError("Response size exceeds maximum limit")
    
    result = json.loads(content)
    
    if response.status_code != 200:
        # Still parse the error from JSON
        pass
    
    return TokenResponse.from_dict(result)


def exchange_token(refresh_token: str, timeout: int = 30) -> Token:
    """
    Exchange refresh token for access token.
    
    Args:
        refresh_token: Refresh token from poll_for_token()
        timeout: Request timeout in seconds
        
    Returns:
        Access token
        
    Raises:
        requests.RequestException: If the request fails
    """
    url = f"{get_base_url()}/token/exchange"
    
    payload = {
        "refresh_token": refresh_token
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "crush",
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=timeout,
        stream=True,  # Enable streaming to limit response size
    )
    response.raise_for_status()
    
    # Read with size limit to prevent memory exhaustion
    content = response.raw.read(MAX_RESPONSE_SIZE + 1)
    if len(content) > MAX_RESPONSE_SIZE:
        raise ValueError("Response size exceeds maximum limit")
    
    data = json.loads(content)
    token = Token.from_dict(data)
    token.set_expires_at()
    
    return token


def introspect_token(access_token: str, timeout: int = 30) -> IntrospectTokenResponse:
    """
    Validate and get information about an access token.
    
    Implements OAuth2 Token Introspection (RFC 7662).
    
    Args:
        access_token: Access token to introspect
        timeout: Request timeout in seconds
        
    Returns:
        Token introspection response
        
    Raises:
        requests.RequestException: If the request fails
    """
    url = f"{get_base_url()}/token/introspect"
    
    payload = {
        "token": access_token
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "crush",
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=timeout,
        stream=True,  # Enable streaming to limit response size
    )
    response.raise_for_status()
    
    # Read with size limit to prevent memory exhaustion
    content = response.raw.read(MAX_RESPONSE_SIZE + 1)
    if len(content) > MAX_RESPONSE_SIZE:
        raise ValueError("Response size exceeds maximum limit")
    
    return IntrospectTokenResponse.from_dict(json.loads(content))
