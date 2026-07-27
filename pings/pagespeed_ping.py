from urllib.parse import urlparse
import requests


def audit_pagespeed(url: str, timeout: int = 15) -> dict:
    """Fetches PageSpeed / Core Web Vitals performance metrics using Google's public PSI API endpoint.

    Falls back cleanly if the API rate-limits or times out.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    result = {
        "domain": domain,
        "performance_score": None,
        "accessibility_score": None,
        "core_web_vitals": {
            "lcp_ms": None,
            "cls": None,
            "inp_ms": None,
        },
        "status": "error",
    }

    # Public Google PageSpeed Insights API URL
    psi_endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{domain}&strategy=mobile"

    try:
        response = requests.get(psi_endpoint, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})

            # Extract Lighthouse Scores (scaled 0-100)
            perf_score = categories.get("performance", {}).get("score")
            access_score = categories.get("accessibility", {}).get("score")

            result["performance_score"] = (
                int(perf_score * 100) if perf_score is not None else None
            )
            result["accessibility_score"] = (
                int(access_score * 100) if access_score is not None else None
            )

            # Extract Core Web Vitals
            audits = lighthouse.get("audits", {})
            lcp = audits.get("largest-contentful-paint", {}).get(
                "numericValue"
            )
            cls = audits.get("cumulative-layout-shift", {}).get("numericValue")
            inp = audits.get("interaction-to-next-paint", {}).get(
                "numericValue"
            )

            result["core_web_vitals"] = {
                "lcp_ms": round(lcp, 2) if lcp else None,
                "cls": round(cls, 3) if cls is not None else None,
                "inp_ms": round(inp, 2) if inp else None,
            }
            result["status"] = "success"
        else:
            result["error"] = (
                f"PageSpeed API HTTP {response.status_code}: Rate limit or domain issue."
            )

    except requests.exceptions.Timeout:
        result["error"] = (
            "PageSpeed API Request Timed Out (took longer than 15s)."
        )
    except Exception as e:
        result["error"] = f"PageSpeed Audit Exception: {str(e)}"

    return result


if __name__ == "__main__":
    print("--- Extended PageSpeed Ping Loaded ---")
