"""
Disk cache management for GitHub Copilot tokens.

Reads tokens from the official GitHub Copilot client's cache.
"""

import json
import os
import platform
from pathlib import Path
from typing import Optional


def refresh_token_from_disk() -> Optional[str]:
    """
    Read refresh token from GitHub Copilot's disk cache.
    
    Reads the token from the official GitHub Copilot client's local storage.
    This allows reusing existing authentication without re-login.
    
    Returns:
        OAuth token if found, None otherwise
    """
    token_path = _get_token_file_path()
    
    if not token_path.exists():
        return None
    
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Look for the specific GitHub App ID
        app_id = "github.com:Iv1.b507a08c87ecfe98"
        if app_id in data:
            return data[app_id].get("oauth_token")
        
        return None
    except (json.JSONDecodeError, KeyError, IOError):
        return None


def _get_token_file_path() -> Path:
    """
    Get the platform-specific path to the token file.
    
    Returns:
        Path to the apps.json file
    """
    system = platform.system()
    
    if system == "Windows":
        base_dir = os.getenv("LOCALAPPDATA", "")
        if not base_dir:
            base_dir = os.path.expanduser("~\\AppData\\Local")
        return Path(base_dir) / "github-copilot" / "apps.json"
    else:
        # Unix-like systems (Linux, macOS)
        home = os.path.expanduser("~")
        return Path(home) / ".config" / "github-copilot" / "apps.json"
