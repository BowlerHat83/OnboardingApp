"""
pings/security_ping.py - Live binary pass/fail check for SSL and HTTPS enforcement.
"""

import requests
from typing import Dict, Any


def check_security_headers(target_url: str) -> Dict[str, Any]:
    """
    Checks target URL for SSL presence and HTTP -> HTTPS redirection.
    """
    if not target_url.startswith("http"):
        target_url = f"https://{target_url}"

    has_ssl = False
    https_enforced = False

    try:
        # Check SSL on HTTPS endpoint
        response = requests.get(target_url, timeout=5)
        has_ssl = target_url.startswith("https") and response.status_code < 400

        # Check HTTP -> HTTPS Redirect
        http_url = target_url.replace("https://", "http://")
        response_http = requests.get(http_url, timeout=5, allow_redirects=False)
        if response_http.status_code in [301, 302, 307, 308]:
            redirect = response_http.headers.get("Location", "")
            if redirect.startswith("https://"):
                https_enforced = True

    except Exception:
        pass  # Network/SSL error = default to False

    return {
        "has_ssl": has_ssl,
        "https_enforced": https_enforced
    }
