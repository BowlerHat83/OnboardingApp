import sys
import time
import json
from concurrent.futures import ThreadPoolExecutor
from pings.ai_readiness_ping import audit_ai_readiness
from pings.gdpr_cookie_ping import audit_gdpr_cookies
from pings.onpage_ping import audit_onpage
from pings.pagespeed_ping import audit_pagespeed
from pings.security_ping import audit_security

def run_all_pings(target_domain):
    print("\n" + "=" * 60)
    print(f" ?? RUNNING FULL PING SUITE FOR: {target_domain}")
    print("=" * 60 + "\n")
    start_time = time.time()
    tasks = {
        "1. Security & Protocol": lambda: audit_security(target_domain),
        "2. AI Readiness": lambda: audit_ai_readiness(target_domain),
        "3. Website Health": lambda: audit_pagespeed(target_domain),
        "4. On-Page SEO & UX": lambda: audit_onpage(target_domain),
        "5. GDPR & Cookie Compliance": lambda: audit_gdpr_cookies(target_domain),
    }
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {executor.submit(task): name for name, task in tasks.items()}
        for future in future_to_name:
            name = future_to_name[future]
            try:
                results[name] = future.result()
                print(f"  ? {name} Completed.")
            except Exception as exc:
                results[name] = {"status": "error", "error": str(exc)}
                print(f"  ? {name} Failed: {exc}")
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 60)
    print(f" ?? CONSOLIDATED AUDIT RESULTS (Completed in {elapsed}s)")
    print("=" * 60 + "\n")
    print(json.dumps(results, indent=2))
    print("\n" + "=" * 60)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    run_all_pings(target)
