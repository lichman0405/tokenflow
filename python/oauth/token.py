"""
Token management module.

Provides OAuth2 token data structure and lifecycle management.
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class Token:
    """
    Represents an OAuth2 token.
    
    Attributes:
        access_token: The access token for API calls
        refresh_token: The refresh token for obtaining new access tokens
        expires_in: Token lifetime in seconds
        expires_at: Unix timestamp when the token expires
    """
    access_token: str
    refresh_token: str = ""
    expires_in: int = 0
    expires_at: int = 0

    def set_expires_at(self) -> None:
        """
        Calculate and set the expires_at field based on current time and expires_in.
        """
        self.expires_at = int(time.time()) + self.expires_in

    def is_expired(self) -> bool:
        """
        Check if the token is expired or about to expire.
        
        Returns True if expired or within 10% of its lifetime from expiration.
        This provides a buffer time for token refresh.
        
        Returns:
            True if the token is expired or about to expire, False otherwise
        """
        buffer = self.expires_in // 10
        return int(time.time()) >= (self.expires_at - buffer)

    def set_expires_in(self) -> None:
        """
        Calculate and set the expires_in field based on expires_at.
        """
        self.expires_in = max(0, self.expires_at - int(time.time()))

    def to_dict(self) -> dict:
        """
        Convert token to dictionary for serialization.
        
        Returns:
            Dictionary representation of the token
        """
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_in": self.expires_in,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        """
        Create a Token instance from a dictionary.
        
        Args:
            data: Dictionary containing token data
            
        Returns:
            Token instance
        """
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            expires_in=data.get("expires_in", 0),
            expires_at=data.get("expires_at", 0),
        )
