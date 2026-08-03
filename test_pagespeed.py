import requests
import json
import time

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TARGET_URL = "https://bowlerhat.co.uk"
# Optional: Add your Google PSI API key here to avoid rate limits
API_KEY = "AIzaSyAoTBm7gD9x_6KsEScS5cif-dT0zBbeSRM"  # e.g., "AIzaSy..." 

def run_pagespeed_check(url: str, strategy: str = "mobile") -> dict | None:
    """
    Calls Google PageSpeed Insights API v5 directly.
    strategy: 'mobile' or 'desktop'
    """
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "seo", "best-practices"]
    }
    
    if API_KEY:
        params["key"] = API_KEY

    print(f"\n[PSI] Requesting {strategy.upper()} PageSpeed report for: {url}...")
    print("      (Google Lighthouse takes ~15-30s to analyze...)")
    
    start_time = time.time()
    try:
        # High timeout (60s) because Lighthouse takes time on Google's servers
        response = requests.get(endpoint, params=params, timeout=60)
        elapsed = round(time.time() - start_time, 2)
        
        print(f"[PSI] Status Code: {response.status_code} (took {elapsed}s)")
        
        if response.status_code != 200:
            print(f"      API Error Response: {response.text[:300]}")
            return None
            
        data = response.json()
        
        # Extract core metrics safely
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})
        
        parsed_summary = {
            "strategy": strategy,
            "scores": {
                "performance": int((categories.get("performance", {}).get("score") or 0) * 100),
                "accessibility": int((categories.get("accessibility", {}).get("score") or 0) * 100),
                "seo": int((categories.get("seo", {}).get("score") or 0) * 100),
                "best_practices": int((categories.get("best-practices", {}).get("score") or 0) * 100),
            },
            "core_web_vitals": {
                "LCP": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                "FID_TBT": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
                "CLS": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
                "FCP": audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
            }
        }
        return parsed_summary

    except requests.exceptions.Timeout:
        print("      ERROR: PageSpeed API call timed out after 60 seconds.")
        return None
    except Exception as e:
        print(f"      ERROR: PageSpeed API failed: {str(e)}")
        return None


if __name__ == "__main__":
    result = run_pagespeed_check(TARGET_URL, strategy="mobile")
    
    if result:
        print("\n================ PAGESPEED DATA RECEIVED ================")
        print(json.dumps(result, indent=2))
        print("========================================================")
    else:
        print("\nPageSpeed test failed.")