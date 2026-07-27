from urllib.parse import urlparse
import requests


def audit_ai_readiness(url: str, timeout: int = 5) -> dict:
    """Checks for machine-readable files (llms.txt) and AI crawler directives in robots.txt.

    Returns a standardized dictionary for Service Area #2 (AI Visibility /
    GEO).
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    result = {
        "domain": domain,
        "llms_txt": {"present": False, "url": f"https://{domain}/llms.txt"},
        "ai_crawlers": {
            "gptbot_allowed": True,
            "claudebot_allowed": True,
            "perplexitybot_allowed": True,
        },
        "score": 0,
    }

    # 1. Check for /llms.txt
    try:
        res = requests.get(
            result["llms_txt"]["url"],
            timeout=timeout,
            headers={"User-Agent": "BowlerHatAuditBot/1.0"},
        )
        result["llms_txt"]["present"] = res.status_code == 200
    except Exception:
        result["llms_txt"]["present"] = False

    # 2. Inspect robots.txt for AI Bot blocks
    try:
        robots_url = f"https://{domain}/robots.txt"
        res = requests.get(
            robots_url,
            timeout=timeout,
            headers={"User-Agent": "BowlerHatAuditBot/1.0"},
        )

        if res.status_code == 200:
            content = res.text.lower()

            # Check if specific bots are disallowed
            if "user-agent: gptbot" in content and "disallow: /" in content:
                result["ai_crawlers"]["gptbot_allowed"] = False
            if "user-agent: claudebot" in content and "disallow: /" in content:
                result["ai_crawlers"]["claudebot_allowed"] = False
            if (
                "user-agent: perplexitybot" in content
                and "disallow: /" in content
            ):
                result["ai_crawlers"]["perplexitybot_allowed"] = False
    except Exception:
        pass  # Default to allowed if robots.txt can't be fetched

    # Calculate AI File Readiness Score (0-100)
    score = 40  # Base score for active domain
    if result["llms_txt"]["present"]:
        score += 30
    if result["ai_crawlers"]["gptbot_allowed"]:
        score += 10
    if result["ai_crawlers"]["claudebot_allowed"]:
        score += 10
    if result["ai_crawlers"]["perplexitybot_allowed"]:
        score += 10

    result["score"] = score
    return result


# Standalone Test Execution
if __name__ == "__main__":
    import json

    test_domain = "github.com"
    print(f"--- Running AI Readiness Ping for {test_domain} ---")
    data = audit_ai_readiness(test_domain)
    print(json.dumps(data, indent=2))
