"""
HTTP headers for GitHub Copilot API requests.

Provides standard headers that mimic the official client.
"""

from typing import Dict


# Constants matching official client
USER_AGENT = "GitHubCopilotChat/0.32.4"
EDITOR_VERSION = "vscode/1.105.1"
EDITOR_PLUGIN_VERSION = "copilot-chat/0.32.4"
INTEGRATION_ID = "vscode-chat"


def get_headers() -> Dict[str, str]:
    """
    Get standard headers for Copilot API requests.
    
    Returns headers that identify the client as VS Code with Copilot Chat.
    
    Returns:
        Dictionary of HTTP headers
    """
    return {
        "User-Agent": USER_AGENT,
        "Editor-Version": EDITOR_VERSION,
        "Editor-Plugin-Version": EDITOR_PLUGIN_VERSION,
        "Copilot-Integration-Id": INTEGRATION_ID,
    }
