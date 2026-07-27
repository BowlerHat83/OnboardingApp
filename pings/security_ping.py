from datetime import datetime, timezone
import socket
import ssl
from urllib.parse import urlparse
import requests


def audit_security(url: str, timeout: int = 5) -> dict:
    """Audits SSL certificate validity, expiration days, and HTTP security headers.

    Returns a standardized dictionary for Service Area #8 (Security).
    """
    # Clean input domain
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    result = {
        "domain": domain,
        "ssl": {
            "valid": False,
            "days_remaining": None,
            "issuer": None,
            "error": None,
        },
        "headers": {
            "hsts": False,
            "csp": False,
            "x_frame_options": False,
            "x_content_type": False,
            "referrer_policy": False,
            "grade_score": 0,
        },
        "protocol": {"https_enforced": False, "http_version": "HTTP/1.1"},
    }

    # 1. SSL Certificate Check via TLS Socket Handshake
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                # Parse expiration date
                expiry_date = datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                ).replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_left = (expiry_date - now).days

                # Issuer extraction
                issuer_info = dict(x[0] for x in cert.get("issuer", []))
                issuer_name = issuer_info.get(
                    "organizationName", "Unknown Issuer"
                )

                result["ssl"]["valid"] = days_left > 0
                result["ssl"]["days_remaining"] = days_left
                result["ssl"]["issuer"] = issuer_name
    except Exception as e:
        result["ssl"]["error"] = f"SSL Connection Failed: {str(e)}"

    # 2. HTTP Headers & Redirect Check
    try:
        # Check HTTP -> HTTPS Enforcement
        http_check = requests.get(
            f"http://{domain}", timeout=timeout, allow_redirects=True
        )
        result["protocol"]["https_enforced"] = http_check.url.startswith(
            "https://"
        )

        # Inspect Security Headers
        response = requests.head(
            f"https://{domain}", timeout=timeout, allow_redirects=True
        )
        headers = {k.lower(): v for k, v in response.headers.items()}

        result["headers"]["hsts"] = "strict-transport-security" in headers
        result["headers"]["csp"] = "content-security-policy" in headers
        result["headers"]["x_frame_options"] = "x-frame-options" in headers
        result["headers"]["x_content_type"] = (
            "x-content-type-options" in headers
        )
        result["headers"]["referrer_policy"] = "referrer-policy" in headers

        # Calculate a quick 0-100 Security Header Score based on header presence
        score = 0
        if result["ssl"]["valid"]:
            score += 30
        if result["protocol"]["https_enforced"]:
            score += 20
        if result["headers"]["hsts"]:
            score += 20
        if result["headers"]["csp"]:
            score += 15
        if result["headers"]["x_frame_options"]:
            score += 15

        result["headers"]["grade_score"] = score

    except Exception as e:
        result["protocol"]["error"] = f"Header Scan Failed: {str(e)}"

    return result


# Standalone Test Execution
if __name__ == "__main__":
    import json

    test_domain = "bowlerhat.co.uk"
    print(f"--- Running Security Ping for {test_domain} ---")
    data = audit_security(test_domain)
    print(json.dumps(data, indent=2))
