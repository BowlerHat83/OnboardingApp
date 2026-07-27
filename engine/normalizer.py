import os
import csv
from typing import Dict, Any
from models.audit_schema import ClientAuditRecord, AuditSection

# Import actual functions from your pings/ directory
from pings.security_ping import audit_security
from pings.ai_readiness_ping import check_ai_readiness
from pings.pagespeed_ping import audit_pagespeed
from pings.onpage_ping import audit_onpage
from pings.gdpr_cookie_ping import audit_gdpr_cookies
from engine.scorer import score_technical_seo


def run_live_pings(domain: str) -> Dict[str, AuditSection]:
    """Runs automated live network pings and maps outputs to AuditSection."""
    results = {}

    # 1. Security Ping
    try:
        sec_raw = audit_security(domain)
        sec_score = sec_raw.get("headers", {}).get("grade_score", 0)
        ssl_valid = sec_raw.get("ssl", {}).get("valid", False)
        days_left = sec_raw.get("ssl", {}).get("days_remaining", "N/A")
        results["security"] = AuditSection(
            score=sec_score,
            status="success" if ssl_valid else "warning",
            findings=[
                f"SSL Valid: {ssl_valid} ({days_left} days remaining)",
                f"HTTPS Enforced: {sec_raw.get('protocol', {}).get('https_enforced', False)}"
            ],
            raw_data=sec_raw
        )
    except Exception as e:
        results["security"] = AuditSection(status="error", findings=[f"Security Ping Failed: {e}"])

    # 2. AI Readiness Ping
    try:
        ai_raw = check_ai_readiness(domain)
        results["ai_readiness"] = AuditSection(
            score=ai_raw.get("score", 70),
            status="success",
            findings=[f"llms.txt Present: {ai_raw.get('llms_txt', False)}"],
            raw_data=ai_raw
        )
    except Exception as e:
        results["ai_readiness"] = AuditSection(status="error", findings=[f"AI Readiness Ping Failed: {e}"])

    # 3. Website Health / PageSpeed Ping
    try:
        speed_raw = audit_pagespeed(domain)
        results["website_health"] = AuditSection(
            score=speed_raw.get("score", 80),
            status="success",
            findings=[f"Performance Grade: {speed_raw.get('score', 80)}"],
            raw_data=speed_raw
        )
    except Exception as e:
        results["website_health"] = AuditSection(status="error", findings=[f"PageSpeed Ping Failed: {e}"])

    # 4. On-Page SEO Ping
    try:
        onpage_raw = audit_onpage(domain)
        results["onpage_seo"] = AuditSection(
            score=onpage_raw.get("score", 75),
            status="success",
            findings=[f"H1 Tag Present: {onpage_raw.get('has_h1', True)}"],
            raw_data=onpage_raw
        )
    except Exception as e:
        results["onpage_seo"] = AuditSection(status="error", findings=[f"On-Page Ping Failed: {e}"])

    # 5. GDPR Cookies Ping
    try:
        gdpr_raw = audit_gdpr_cookies(domain)
        results["gdpr_cookies"] = AuditSection(
            score=gdpr_raw.get("score", 50),
            status="success",
            findings=[f"Risk Level: {gdpr_raw.get('risk_level', 'Medium')}"],
            raw_data=gdpr_raw
        )
    except Exception as e:
        results["gdpr_cookies"] = AuditSection(status="error", findings=[f"GDPR Ping Failed: {e}"])

    return results


def parse_csv_files(csv_dir: str) -> Dict[str, Any]:
    """Scans input_csvs/ directory and extracts crawl/analytics metrics."""
    parsed_data = {
        "technical_seo": {"status_404": 0, "non_indexable": 0, "total_urls": 0},
        "analytics": {"engagement_rate": None, "bounce_rate": None}
    }

    if not os.path.exists(csv_dir):
        return parsed_data

    for fname in os.listdir(csv_dir):
        if not fname.endswith(".csv"):
            continue
        filepath = os.path.join(csv_dir, fname)
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header_row = next(reader, None)
                if not header_row:
                    continue
                headers = [h.strip().lower() for h in header_row]

                # Screaming Frog / Technical Crawl CSV
                if "address" in headers and ("status code" in headers or "indexability" in headers):
                    f.seek(0)
                    dict_reader = csv.DictReader(f)
                    total = 0
                    errors = 0
                    non_index = 0
                    for row in dict_reader:
                        total += 1
                        code = str(row.get("Status Code", "")).strip()
                        indexability = str(row.get("Indexability", "")).strip()
                        if code in ["404", "500", "502", "503"]:
                            errors += 1
                        if indexability.lower() == "non-indexable":
                            non_index += 1

                    parsed_data["technical_seo"] = {
                        "status_404": errors,
                        "non_indexable": non_index,
                        "total_urls": total
                    }
        except Exception as e:
            print(f"   ⚠️ Warning parsing {fname}: {e}")

    return parsed_data


def run_full_client_audit(domain: str, csv_dir: str = "input_csvs") -> ClientAuditRecord:
    """Executes network pings and incorporates CSV input data into ClientAuditRecord."""
    # 1. Fetch Live Automated Pings
    live_results = run_live_pings(domain)

    # 2. Parse Dropzone CSV Exports
    csv_data = parse_csv_files(csv_dir)

    # 3. Process Section 6: Technical SEO from CSV
    tech_info = csv_data["technical_seo"]
    if tech_info["total_urls"] > 0:
        total = tech_info["total_urls"]
        errors = tech_info["status_404"]
        score = score_technical_seo(total, errors, tech_info['non_indexable'])
        findings = [
            f"Total Crawled URLs: {total}",
            f"Broken Links / Errors (4xx/5xx): {errors}",
            f"Non-Indexable Pages: {tech_info['non_indexable']}"
        ]
        sec_technical = AuditSection(
            score=score,
            status="success",
            findings=findings,
            raw_data=tech_info
        )
    else:
        sec_technical = AuditSection(
            score=None,
            status="pending",
            findings=["No Screaming Frog or crawl CSV uploaded to input_csvs/"]
        )

    # Construct Complete Record adhering to audit_schema.py
    record = ClientAuditRecord(
        client_domain=domain,
        security=live_results.get("security", AuditSection()),
        ai_readiness=live_results.get("ai_readiness", AuditSection()),
        website_health=live_results.get("website_health", AuditSection()),
        onpage_seo=live_results.get("onpage_seo", AuditSection()),
        gdpr_cookies=live_results.get("gdpr_cookies", AuditSection()),
        technical_seo=sec_technical,
        analytics_tracking=AuditSection(status="pending", findings=["No Analytics CSV found"]),
        content_strategy=AuditSection(status="pending", findings=["No Content CSV found"]),
        cro_ux=AuditSection(status="pending", findings=["No CRO CSV found"])
    )

    record.calculate_overall_score()
    return record