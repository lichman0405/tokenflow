"""
GitHub Copilot OAuth device flow implementation.

Implements the OAuth2 device authorization flow for GitHub Copilot.
"""

from dataclasses import dataclass
from typing import Optional
import json
import time
import requests
from urllib.parse import urlencode

from ..token import Token
from .http import get_headers


# GitHub OAuth endpoints
CLIENT_ID = "Iv1.b507a08c87ecfe98"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"

# Maximum response size (1MB) to prevent memory exhaustion
MAX_RESPONSE_SIZE = 1024 * 1024

# Custom exceptions
class NotAvailableError(Exception):
    """Raised when GitHub Copilot is not available for the user."""
    pass


@dataclass
class DeviceCode:
    """
    Device code response from GitHub.
    
    Attributes:
        device_code: Code used for polling
        user_code: Code displayed to the user
        verification_uri: URL where user authorizes the device
        expires_in: Seconds until the device code expires
        interval: Minimum polling interval in seconds
    """
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceCode":
        """Create DeviceCode from API response."""
        return cls(
            device_code=data["device_code"],
            user_code=data["user_code"],
            verification_uri=data["verification_uri"],
            expires_in=data["expires_in"],
            interval=data.get("interval", 5),
        )


def request_device_code(timeout: int = 30) -> DeviceCode:
    """
    Initiate the device code flow with GitHub.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        DeviceCode containing user_code and verification_uri
        
    Raises:
        requests.RequestException: If the request fails
    """
    data = {
        "client_id": CLIENT_ID,
        "scope": "read:user",
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": get_headers()["User-Agent"],
    }
    
    response = requests.post(
        DEVICE_CODE_URL,
        data=urlencode(data),
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    
    return DeviceCode.from_dict(response.json())


def poll_for_token(device_code: DeviceCode, timeout: Optional[int] = None) -> Token:
    """
    Poll GitHub for the access token after user authorization.
    
    Args:
        device_code: DeviceCode obtained from request_device_code()
        timeout: Maximum time to poll in seconds (defaults to device_code.expires_in)
        
    Returns:
        Token containing access and refresh tokens
        
    Raises:
        TimeoutError: If authorization times out
        requests.RequestException: If the request fails
        NotAvailableError: If Copilot is not available
    """
    interval = max(device_code.interval, 5)
    deadline = time.time() + (timeout or device_code.expires_in)
    
    while time.time() < deadline:
        try:
            token = _try_get_token(device_code.device_code)
            if token:
                return token
        except _PendingError:
            time.sleep(interval)
            continue
        except _SlowDownError:
            interval += 5
            time.sleep(interval)
            continue
    
    raise TimeoutError("Authorization timed out")


class _PendingError(Exception):
    """Authorization is pending."""
    pass


class _SlowDownError(Exception):
    """Polling too fast, slow down."""
    pass


def _try_get_token(device_code: str) -> Optional[Token]:
    """
    Try to get the access token from GitHub.
    
    Args:
        device_code: The device code for polling
        
    Returns:
        Token if authorization is complete, None otherwise
        
    Raises:
        _PendingError: If authorization is still pending
        _SlowDownError: If we need to slow down polling
        NotAvailableError: If Copilot is not available
    """
    data = {
        "client_id": CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": get_headers()["User-Agent"],
    }
    
    response = requests.post(
        ACCESS_TOKEN_URL,
        data=urlencode(data),
        headers=headers,
        timeout=30,
    )
    
    result = response.json()
    error = result.get("error", "")
    
    if error == "authorization_pending":
        raise _PendingError()
    elif error == "slow_down":
        raise _SlowDownError()
    elif error:
        raise Exception(f"Authorization failed: {error}")
    
    access_token = result.get("access_token", "")
    if not access_token:
        raise _PendingError()
    
    return _get_copilot_token(access_token)


def _get_copilot_token(github_token: str) -> Token:
    """
    Exchange GitHub token for Copilot token.
    
    Args:
        github_token: GitHub OAuth access token
        
    Returns:
        Copilot token
        
    Raises:
        NotAvailableError: If Copilot is not available
        requests.RequestException: If the request fails
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {github_token}",
        **get_headers(),
    }
    
    response = requests.get(
        COPILOT_TOKEN_URL,
        headers=headers,
        timeout=30,
        stream=True,  # Enable streaming to limit response size
    )
    
    if response.status_code == 403:
        raise NotAvailableError("GitHub Copilot is not available for this account")
    
    response.raise_for_status()
    
    # Read with size limit to prevent memory exhaustion
    content = response.raw.read(MAX_RESPONSE_SIZE + 1)
    if len(content) > MAX_RESPONSE_SIZE:
        raise ValueError("Response size exceeds maximum limit")
    
    result = json.loads(content)
    
    token = Token(
        access_token=result["token"],
        refresh_token=github_token,
        expires_at=result["expires_at"],
    )
    token.set_expires_in()
    
    return token


def refresh_token(github_token: str) -> Token:
    """
    Refresh the Copilot token using the GitHub token.
    
    Args:
        github_token: GitHub OAuth token (stored as refresh_token)
        
    Returns:
        New Copilot token
        
    Raises:
        NotAvailableError: If Copilot is not available
        requests.RequestException: If the request fails
    """
    return _get_copilot_token(github_token)
