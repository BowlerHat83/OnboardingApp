import os
import glob
import json
import time
import subprocess
import requests
import pandas as pd

from app.parsers.screaming_frog import ScreamingFrogParser

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TARGET_URL = "https://bowlerhat.co.uk"
EXPORT_DIR = os.path.abspath("temp_exports")
SF_CLI_PATH = r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"
PSI_API_KEY = "AIzaSyAoTBm7gD9x_6KsEScS5cif-dT0zBbeSRM"  # Add your API key here


# ---------------------------------------------------------
# 1. SCREAMING FROG COLLECTOR
# ---------------------------------------------------------
def collect_screaming_frog_data(url: str) -> dict | None:
    print(f"\n[1/2] Running Screaming Frog CLI for: {url}")
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    cmd = [
        SF_CLI_PATH,
        "--headless",
        "--crawl", url,
        "--output-folder", EXPORT_DIR,
        "--export-tabs", "Internal:All",
        "--overwrite"
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if res.returncode != 0:
            print(f"      [SF ERROR] Exit code {res.returncode}")
            return None
            
        csv_files = glob.glob(os.path.join(EXPORT_DIR, "**", "*.csv"), recursive=True)
        if not csv_files:
            print("      [SF ERROR] No CSV generated.")
            return None
            
        parser = ScreamingFrogParser(csv_filepath=csv_files[0])
        df = parser.parse()
        
        print(f"      [SF SUCCESS] Parsed {len(df)} crawl URLs.")
        return {
            "total_urls_crawled": len(df),
            "status_200_count": len(df[df['status_code'] == 200]) if 'status_code' in df.columns else 0,
            "sample_urls": df['url'].head(5).tolist() if 'url' in df.columns else []
        }
    except Exception as e:
        print(f"      [SF EXCEPTION] {str(e)}")
        return None


# ---------------------------------------------------------
# 2. PAGESPEED INSIGHTS COLLECTOR
# ---------------------------------------------------------
def collect_pagespeed_data(url: str, strategy: str = "mobile") -> dict | None:
    print(f"\n[2/2] Requesting {strategy.upper()} PageSpeed report for: {url}")
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    # Passing parameters as a list of tuples ensures Google gets multiple 'category' params properly
    params = [
        ("url", url),
        ("strategy", strategy),
        ("category", "performance"),
        ("category", "accessibility"),
        ("category", "seo"),
        ("category", "best-practices"),
    ]
    
    # Attach API key if set
    if PSI_API_KEY and PSI_API_KEY != "YOUR_PAGESPEED_API_KEY":
        params.append(("key", PSI_API_KEY.strip()))

    try:
        start_time = time.time()
        res = requests.get(endpoint, params=params, timeout=60)
        elapsed = round(time.time() - start_time, 2)
        
        if res.status_code != 200:
            print(f"      [PSI ERROR] Status {res.status_code}")
            # THIS LINE PRINTS GOOGLE'S EXACT ERROR MESSAGE:
            print(f"      [PSI DETAILS] {res.text[:300]}")
            return None
            
        data = res.json()
        lh = data.get("lighthouseResult", {})
        cats = lh.get("categories", {})
        audits = lh.get("audits", {})
        
        print(f"      [PSI SUCCESS] Completed in {elapsed}s.")
        return {
            "strategy": strategy,
            "scores": {
                "performance": int((cats.get("performance", {}).get("score") or 0) * 100),
                "accessibility": int((cats.get("accessibility", {}).get("score") or 0) * 100),
                "seo": int((cats.get("seo", {}).get("score") or 0) * 100),
                "best_practices": int((cats.get("best-practices", {}).get("score") or 0) * 100),
            },
            "core_web_vitals": {
                "LCP": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                "FID_TBT": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
                "CLS": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
                "FCP": audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
            }
        }
    except Exception as e:
        print(f"      [PSI EXCEPTION] {str(e)}")
        return None
    
# ---------------------------------------------------------
# MASTER PIPELINE EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    print("================ STARTING AUDIT DATA PIPELINE ================")
    
    master_audit_payload = {
        "target_url": TARGET_URL,
        "screaming_frog": collect_screaming_frog_data(TARGET_URL),
        "pagespeed": collect_pagespeed_data(TARGET_URL)
    }
    
    print("\n================ FINAL MASTER AUDIT PAYLOAD ================")
    print(json.dumps(master_audit_payload, indent=2))
    print("============================================================")