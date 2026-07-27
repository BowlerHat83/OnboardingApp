import os
import requests


def audit_pagespeed(url: str, api_key: str = None) -> dict:
    """Queries Google PageSpeed Insights API (Free) for Performance & Accessibility scores.

    Returns a standardized dictionary for Service Area #4 (Web Health) &
    #7 (Accessibility).
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Default structure
    result = {
        "domain": url,
        "performance_score": 0,
        "accessibility_score": 0,
        "core_web_vitals": {
            "lcp_ms": None,  # Largest Contentful Paint
            "cls": None,  # Cumulative Layout Shift
            "inp_ms": None,  # Interaction to Next Paint
        },
        "status": "error",
    }

    # Endpoint URL (No API key needed for basic usage, but supported if added)
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "category": ["PERFORMANCE", "ACCESSIBILITY"],
        "strategy": "MOBILE",
    }

    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})

            # Extract 0-100 Scores (Google returns 0.0 to 1.0)
            perf_raw = categories.get("performance", {}).get("score", 0) or 0
            access_raw = (
                categories.get("accessibility", {}).get("score", 0) or 0
            )

            result["performance_score"] = int(perf_raw * 100)
            result["accessibility_score"] = int(access_raw * 100)

            # Extract Core Web Vitals (Lab Data)
            result["core_web_vitals"]["lcp_ms"] = audits.get(
                "largest-contentful-paint", {}
            ).get("numericValue")
            result["core_web_vitals"]["cls"] = audits.get(
                "cumulative-layout-shift", {}
            ).get("numericValue")
            result["core_web_vitals"]["inp_ms"] = audits.get(
                "total-blocking-time", {}
            ).get("numericValue")  # TBT as INP proxy

            result["status"] = "success"
    except Exception as e:
        result["error"] = str(e)

    return result


# Standalone Test Execution
if __name__ == "__main__":
    import json

    test_url = "bowlerhat.co.uk"
    print(f"--- Running PageSpeed API Ping for {test_url} ---")
    data = audit_pagespeed(test_url)
    print(json.dumps(data, indent=2))
