from urllib.parse import urlparse
import requests


def check_ai_readiness(url: str, timeout: int = 5) -> dict:
    """Checks for the presence of /llms.txt and inspects robots.txt for AI crawler permissions.

    Returns data for Service Area #2 (AI Visibility & GEO).
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    base_url = f"{parsed.scheme}://{domain}"

    result = {
        "domain": domain,
        "has_llms_txt": False,
        "has_robots_txt": False,
        "ai_crawlers_allowed": True,
        "blocked_ai_bots": [],
        "ai_score": 50,
        "status": "error",
    }

    ai_bots = [
        "GPTBot",
        "ChatGPT-User",
        "ClaudeBot",
        "PerplexityBot",
        "Google-Extended",
    ]

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BowlerHatAuditBot/1.0"
        }

        # 1. Check for /llms.txt
        try:
            llms_res = requests.get(
                f"{base_url}/llms.txt", timeout=timeout, headers=headers
            )
            if (
                llms_res.status_code == 200
                and "text/plain" in llms_res.headers.get("Content-Type", "")
            ):
                result["has_llms_txt"] = True
        except Exception:
            pass

        # 2. Check /robots.txt for AI Bot restrictions
        try:
            robots_res = requests.get(
                f"{base_url}/robots.txt", timeout=timeout, headers=headers
            )
            if robots_res.status_code == 200:
                result["has_robots_txt"] = True
                content = robots_res.text.lower()

                for bot in ai_bots:
                    if f"user-agent: {bot.lower()}" in content:
                        # Simple check if Disallow follows
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if line.strip() == f"user-agent: {bot.lower()}":
                                if (
                                    i + 1 < len(lines)
                                    and "disallow: /" in lines[i + 1].strip()
                                ):
                                    result["blocked_ai_bots"].append(bot)

                if result["blocked_ai_bots"]:
                    result["ai_crawlers_allowed"] = False
        except Exception:
            pass

        # Score calculation
        score = 50
        if result["has_llms_txt"]:
            score += 30
        if result["has_robots_txt"] and result["ai_crawlers_allowed"]:
            score += 20
        elif not result["ai_crawlers_allowed"]:
            score -= 20

        result["ai_score"] = max(0, min(100, score))
        result["status"] = "success"

    except Exception as e:
        result["error"] = f"AI Readiness Scan Error: {str(e)}"

    return result


if __name__ == "__main__":
    print("--- AI Readiness Ping Loaded ---")
