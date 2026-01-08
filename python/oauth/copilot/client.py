"""
HTTP client with custom request interceptor.

Provides HTTP client that automatically adds X-Initiator header
based on request body content.
"""

import re
from typing import Optional
import requests
from requests.adapters import HTTPAdapter


# Pre-compiled regex pattern for better performance
_ASSISTANT_PATTERN = re.compile(r'"role"\s*:\s*"assistant"')


class InitiatorAdapter(HTTPAdapter):
    """
    HTTP adapter that adds X-Initiator header based on request body.
    
    Inspects the request body for assistant messages and sets the
    X-Initiator header accordingly:
    - "agent" if assistant messages are found or is_sub_agent is True
    - "user" otherwise
    """
    
    def __init__(self, is_sub_agent: bool = False, debug: bool = False, *args, **kwargs):
        """
        Initialize the adapter.
        
        Args:
            is_sub_agent: If True, always set X-Initiator to "agent"
            debug: Enable debug logging
        """
        super().__init__(*args, **kwargs)
        self.is_sub_agent = is_sub_agent
        self.debug = debug
    
    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        """
        Send a request with X-Initiator header injected.
        
        Overrides HTTPAdapter.send() to inject the header before sending.
        
        Args:
            request: PreparedRequest object
            stream: Whether to stream the response
            timeout: Request timeout
            verify: SSL verification
            cert: Client certificate
            proxies: Proxy settings
            
        Returns:
            Response object
        """
        initiator = "user"
        
        # Check if request has a body
        if request.body:
            try:
                # Handle both string and bytes
                body_data = request.body
                if isinstance(body_data, bytes):
                    body_str = body_data.decode('utf-8')
                else:
                    body_str = str(body_data)
                
                # Check for assistant messages using regex
                if _ASSISTANT_PATTERN.search(body_str) or self.is_sub_agent:
                    initiator = "agent"
            except (UnicodeDecodeError, AttributeError):
                pass
        elif self.is_sub_agent:
            initiator = "agent"
        
        request.headers["X-Initiator"] = initiator
        
        if self.debug:
            print(f"Setting X-Initiator header to: {initiator}")
        
        return super().send(request, stream=stream, timeout=timeout, 
                           verify=verify, cert=cert, proxies=proxies)


def create_client(is_sub_agent: bool = False, debug: bool = False) -> requests.Session:
    """
    Create a new HTTP client with custom transport.
    
    Args:
        is_sub_agent: If True, always set X-Initiator to "agent"
        debug: Enable debug logging
        
    Returns:
        Configured requests.Session
    """
    session = requests.Session()
    adapter = InitiatorAdapter(is_sub_agent=is_sub_agent, debug=debug)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
