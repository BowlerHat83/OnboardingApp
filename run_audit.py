import os
import sys
import json
import argparse
from engine.normalizer import run_full_client_audit

def main():
    parser = argparse.ArgumentParser(description="OnboardingApp Audit Engine")
    parser.add_argument("domain", help="Target client domain")
    parser.add_argument("--csv-dir", default="input_csvs", help="CSV directory")
    parser.add_argument("--save", action="store_true", help="Save JSON report")
    args = parser.parse_args()
    domain = args.domain

    print("\n" + "=" * 60)
    print(f" 🚀 ONBOARDINGAPP AUDIT ENGINE - TARGET: {domain}")
    print("=" * 60 + "\n")

    csv_dir = args.csv_dir
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir, exist_ok=True)

    csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]
    print(f" 📁 Input CSV Directory: {os.path.abspath(csv_dir)}")
    print(f" 📄 Found {len(csv_files)} CSV file(s)\n")

    print(" ⏳ Running Automated Live Pings...")
    record = run_full_client_audit(domain)

    print("\n" + "=" * 60)
    print(f" 📊 AUDIT SUMMARY FOR: {domain}")
    print(f" ⭐ OVERALL SCORE: {record.overall_score}/100")
    print("=" * 60 + "\n")

    sections = [
        ("1. Security", record.security),
        ("2. AI Readiness", record.ai_readiness),
        ("3. Website Health", record.website_health),
        ("4. On-Page SEO", record.onpage_seo),
        ("5. GDPR Cookies", record.gdpr_cookies),
        ("6. Technical SEO", record.technical_seo),
        ("7. Analytics", record.analytics_tracking),
        ("8. Content Strategy", record.content_strategy),
        ("9. CRO UX", record.cro_ux),
    ]

    for title, sec in sections:
        score_str = f"{sec.score}/100" if sec.score is not None else "Pending (Upload CSV)"
        print(f" [{sec.status.upper():^10}] {title:<25} Score: {score_str}")
        for f in sec.findings:
            print(f"             • {f}")

    print("\n" + "=" * 60)

    if args.save:
        fname = f"audit_{domain.replace('.', '_')}.json"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))
        print(f" 💾 Saved report to: {fname}\n")

if __name__ == "__main__":
    main()