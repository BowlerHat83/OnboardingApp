from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def audit_gdpr_cookies(url: str, timeout: int = 5) -> dict:
    """Scans website for GDPR/ePrivacy consent management, cookie banner scripts,
    tracking script auto-blocking, and privacy policy links.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    result = {
        "domain": domain,
        "cmp_detected": None,
        "has_cmp": False,
        "privacy_policy_found": False,
        "unblocked_trackers_detected": [],
        "gdpr_risk_level": "LOW",
        "compliance_score": 0,
        "status": "error",
    }

    cmp_signatures = {
        "CookieBot": ["cookiebot.com", "uc.js"],
        "OneTrust": ["onetrust.com", "otbanner"],
        "CookieYes": ["cookieyes.com"],
        "Usercentrics": ["usercentrics.eu"],
        "Iubenda": ["iubenda.com"],
        "Civic Cookie Control": ["civiccomputing.com"],
    }

    tracker_signatures = {
        "Google Analytics / Tag Manager": ["googletagmanager.com", "google-analytics.com"],
        "Meta / Facebook Pixel": ["connect.facebook.net"],
        "Hotjar": ["hotjar.com"],
    }

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BowlerHatAuditBot/1.0"
            },
        )

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            html_str = response.text.lower()

            # 1. Detect CMP / Cookie Banner
            for cmp_name, sigs in cmp_signatures.items():
                if any(sig in html_str for sig in sigs):
                    result["cmp_detected"] = cmp_name
                    result["has_cmp"] = True
                    break

            # 2. Check for Privacy/Cookie Policy Links
            for link in soup.find_all("a", href=True):
                href = link["href"].lower()
                text = link.get_text().lower()
                if any(k in href or k in text for k in ["privacy", "cookie", "gdpr"]):
                    result["privacy_policy_found"] = True
                    break

            # 3. Check for Unblocked Prior-Consent Tracking Scripts
            for tracker_name, sigs in tracker_signatures.items():
                if any(sig in html_str for sig in sigs):
                    result["unblocked_trackers_detected"].append(tracker_name)

            # Determine Risk Level & Score
            score = 100
            if not result["has_cmp"]:
                score -= 40
            if not result["privacy_policy_found"]:
                score -= 30
            if result["unblocked_trackers_detected"] and not result["has_cmp"]:
                score -= 30

            result["compliance_score"] = max(0, score)

            if result["compliance_score"] >= 80:
                result["gdpr_risk_level"] = "LOW"
            elif result["compliance_score"] >= 50:
                result["gdpr_risk_level"] = "MEDIUM"
            else:
                result["gdpr_risk_level"] = "HIGH"

            result["status"] = "success"

    except Exception as e:
        result["error"] = f"GDPR Scan Error: {str(e)}"

    return result
