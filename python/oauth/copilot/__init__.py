"""
GitHub Copilot integration module.

Provides device flow authentication for GitHub Copilot.
"""

from .oauth import (
    DeviceCode,
    request_device_code,
    poll_for_token,
    refresh_token,
    NotAvailableError,
)
from .disk import refresh_token_from_disk
from .client import create_client
from .urls import SIGNUP_URL, FREE_URL

__all__ = [
    "DeviceCode",
    "request_device_code",
    "poll_for_token",
    "refresh_token",
    "refresh_token_from_disk",
    "create_client",
    "NotAvailableError",
    "SIGNUP_URL",
    "FREE_URL",
]
