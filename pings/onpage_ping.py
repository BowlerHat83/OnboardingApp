from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def audit_onpage(url: str, timeout: int = 5) -> dict:
    """Scans the target URL DOM for On-Page SEO (Headings, Meta, Word Count)
    and UX/Conversion elements (CTAs, Forms, Contact Links).
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    result = {
        "domain": domain,
        "headings": {
            "h1_count": 0,
            "h2_count": 0,
            "h1_text": None,
            "has_single_h1": False,
        },
        "content": {
            "word_count": 0,
            "has_meta_description": False,
            "meta_description": None,
        },
        "conversion_ux": {
            "form_count": 0,
            "has_phone_link": False,
            "has_email_link": False,
            "has_viewport_tag": False,
        },
        "score": 0,
        "status": "error",
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

            # 1. Heading Structure
            h1s = soup.find_all("h1")
            h2s = soup.find_all("h2")
            result["headings"]["h1_count"] = len(h1s)
            result["headings"]["h2_count"] = len(h2s)
            result["headings"]["has_single_h1"] = len(h1s) == 1
            if h1s:
                result["headings"]["h1_text"] = h1s[0].get_text(strip=True)

            # 2. Content & Meta Tags
            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if meta_desc and meta_desc.get("content"):
                result["content"]["has_meta_description"] = True
                result["content"]["meta_description"] = meta_desc.get("content")

            # Word count
            body = soup.find("body")
            if body:
                text = body.get_text(separator=" ", strip=True)
                result["content"]["word_count"] = len(text.split())

            # 3. Conversion & UX Elements
            result["conversion_ux"]["form_count"] = len(soup.find_all("form"))
            result["conversion_ux"]["has_phone_link"] = bool(
                soup.find("a", href=lambda h: h and "tel:" in h.lower())
            )
            result["conversion_ux"]["has_email_link"] = bool(
                soup.find("a", href=lambda h: h and "mailto:" in h.lower())
            )
            result["conversion_ux"]["has_viewport_tag"] = bool(
                soup.find("meta", attrs={"name": "viewport"})
            )

            # Score Calculation (0-100)
            score = 20
            if result["headings"]["has_single_h1"]:
                score += 25
            if result["content"]["has_meta_description"]:
                score += 25
            if result["content"]["word_count"] >= 300:
                score += 15
            if (
                result["conversion_ux"]["form_count"] > 0
                or result["conversion_ux"]["has_phone_link"]
            ):
                score += 15

            result["score"] = score
            result["status"] = "success"

    except Exception as e:
        result["error"] = f"On-Page Scan Error: {str(e)}"

    return result
