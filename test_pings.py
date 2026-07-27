import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Flexible import so it works with either function name in ai_readiness_ping.py
try:
    from pings.ai_readiness_ping import audit_ai_readiness as check_ai_readiness
except ImportError:
    try:
        from pings.ai_readiness_ping import check_ai_readiness
    except ImportError as e:
        print(f"❌ Import Error in ai_readiness_ping: {e}")
        sys.exit(1)

# Import remaining pings
try:
    from pings.gdpr_cookie_ping import audit_gdpr_cookies
    from pings.onpage_ping import audit_onpage
    from pings.pagespeed_ping import get_pagespeed_metrics
    from pings.security_ping import audit_security
except ImportError as e:
    print(
        f"❌ Import Error: Make sure you run this script from the root 'OnboardingApp' directory.\nDetail: {e}"
    )
    sys.exit(1)


def run_all_pings(target_domain: str):
    """Executes all 5 automated pings concurrently against a target domain and pretty-prints the consolidated output."""
    print("\n" + "=" * 60)
    print(f" 🚀 RUNNING FULL PING SUITE FOR: {target_domain}")
    print("=" * 60 + "\n")

    start_time = time.time()

    # Define tasks for concurrent execution
    tasks = {
        "1. Security & Protocol": lambda: audit_security(target_domain),
        "2. AI Readiness (robots/llms.txt)": lambda: check_ai_readiness(
            target_domain
        ),
        "3. Website Health & Core Web Vitals": lambda: get_pagespeed_metrics(
            target_domain
        ),
        "4. On-Page SEO & UX": lambda: audit_onpage(target_domain),
        "5. GDPR & Cookie Compliance": lambda: audit_gdpr_cookies(
            target_domain
        ),
    }

    results = {}

    # Run pings in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {
            executor.submit(task): name for name, task in tasks.items()
        }
        for future in future_to_name:
            name = future_to_name[future]
            try:
                data = future.result()
                results[name] = data
                print(f"  ✅ {name} Completed.")
            except Exception as exc:
                results[name] = {"status": "error", "error": str(exc)}
                print(f"  ❌ {name} Failed: {exc}")

    elapsed = round(time.time() - start_time, 2)

    # Pretty-print the aggregated results
    print("\n" + "=" * 60)
    print(f" 📊 CONSOLIDATED AUDIT RESULTS (Completed in {elapsed}s)")
    print("=" * 60 + "\n")

    print(json.dumps(results, indent=2))
    print("\n" + "=" * 60)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    run_all_pings(target)
