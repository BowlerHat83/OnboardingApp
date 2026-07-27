import os
import glob
from typing import Dict, Any, List
from models.audit_schema import ClientAuditRecord, AuditSection

# Live Network Pings
from pings.security_ping import audit_security
from pings.ai_readiness_ping import check_ai_readiness
from pings.pagespeed_ping import audit_pagespeed
from pings.onpage_ping import audit_onpage
from pings.gdpr_cookie_ping import audit_gdpr_cookies

# OOP CSV Parsers (Phase 1 Vendors)
from parsers.screaming_frog_parser import ScreamingFrogParser
from parsers.semrush_parser import SemrushParser
from parsers.spyfu_parser import SpyFuParser
from parsers.brightlocal_parser import BrightLocalParser
from parsers.waikay_parser import WaikayParser

# Scoring Engine
from engine.scorer import (
    score_technical_seo,
    score_organic_search,
    score_ppc_ads,
    score_local_seo,
)


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


def parse_vendor_csvs(csv_dir: str) -> Dict[str, Any]:
    """
    Scans csv_dir using Phase 1 vendor parser classes:
    - ScreamingFrogParser
    - SemrushParser
    - SpyFuParser
    - BrightLocalParser
    - WaikayParser
    """
    parsed_results = {
        "screaming_frog": None,
        "semrush": None,
        "spyfu": None,
        "brightlocal": None,
        "waikay": None,
    }

    if not os.path.exists(csv_dir):
        return parsed_results

    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))

    parser_classes = [
        ("screaming_frog", ScreamingFrogParser),
        ("semrush", SemrushParser),
        ("spyfu", SpyFuParser),
        ("brightlocal", BrightLocalParser),
        ("waikay", WaikayParser),
    ]

    for filepath in csv_files:
        for key, ParserCls in parser_classes:
            if parsed_results[key] is not None:
                continue  # Already parsed a valid file for this vendor

            try:
                parser_inst = ParserCls(filepath)
                res = parser_inst.parse()
                if res.get("status") == "success":
                    parsed_results[key] = res
            except Exception as e:
                print(f"Error executing {ParserCls.__name__} on {filepath}: {e}")

    return parsed_results


def run_full_client_audit(domain: str, csv_dir: str = "input_csvs") -> ClientAuditRecord:
    """Executes network pings and incorporates Phase 1 vendor CSV exports."""
    # 1. Fetch Live Automated Pings
    live_results = run_live_pings(domain)

    # 2. Parse Vendor CSV Exports
    csv_data = parse_vendor_csvs(csv_dir)

    # --- Technical SEO (Screaming Frog) ---
    sf_data = csv_data.get("screaming_frog")
    if sf_data and sf_data.get("status") == "success":
        m = sf_data.get("metrics", {})
        total_issues = m.get("total_issues", 0)
        errors = m.get("broken_links_404", 0) + m.get("high_priority_errors", 0)
        non_idx = m.get("non_indexable_url_count", 0)

        score = score_technical_seo(total_issues, errors, non_idx)
        sec_technical = AuditSection(
            score=score,
            status="success",
            findings=[
                f"Total Issues Flagged: {total_issues}",
                f"High-Priority Errors / 404s: {errors}",
                f"Missing Page Titles: {m.get('missing_titles', 0)}",
                f"Missing H1 Headers: {m.get('missing_h1s', 0)}",
                f"Non-Indexable URLs: {non_idx}",
            ],
            raw_data=sf_data
        )
    else:
        sec_technical = AuditSection(
            score=None,
            status="pending",
            findings=["No Screaming Frog CSV found in input_csvs/"]
        )

    # --- Organic Search & Strategy (SEMrush) ---
    semrush_data = csv_data.get("semrush")
    if semrush_data and semrush_data.get("status") == "success":
        m = semrush_data.get("metrics", {})
        total_kw = m.get("total_keywords", 0)
        p2_opps = m.get("page_2_opportunities", 0)
        score = score_organic_search(total_kw, p2_opps)
        sec_content = AuditSection(
            score=score,
            status="success",
            findings=[
                f"Total Keywords Tracked: {total_kw:,}",
                f"Page 2 Opportunity Keywords (Positions 11-20): {p2_opps}",
                f"Top Keywords: {', '.join(m.get('top_keywords', [])[:3])}",
                f"Competitors Identified: {len(m.get('competitors', []))}"
            ],
            raw_data=semrush_data
        )
    else:
        sec_content = AuditSection(
            score=None,
            status="pending",
            findings=["No SEMrush CSV found in input_csvs/"]
        )

    # --- PPC & Paid Search (SpyFu) ---
    spyfu_data = csv_data.get("spyfu")
    if spyfu_data and spyfu_data.get("status") == "success":
        m = spyfu_data.get("metrics", {})
        paid_kw = m.get("total_paid_keywords", 0)
        spend = m.get("est_monthly_spend", 0.0)
        avg_cpc = m.get("avg_cpc", 0.0)
        competitors = m.get("top_ppc_competitors", [])

        score = score_ppc_ads(paid_kw, spend)
        sec_analytics = AuditSection(
            score=score,
            status="success",
            findings=[
                f"Paid Keywords Tracked: {paid_kw:,}",
                f"Estimated Monthly Spend: ${spend:,.2f}",
                f"Average CPC: ${avg_cpc:.2f}",
                f"Top PPC Competitors: {', '.join(competitors[:3]) if competitors else 'None identified'}"
            ],
            raw_data=spyfu_data
        )
    else:
        sec_analytics = AuditSection(
            score=None,
            status="pending",
            findings=["No SpyFu PPC CSV found in input_csvs/"]
        )

    # --- Local SEO & Citations (BrightLocal) ---
    bl_data = csv_data.get("brightlocal")
    if bl_data and bl_data.get("status") == "success":
        m = bl_data.get("metrics", {})
        gbp_score = m.get("gbp_health_score", 0)
        map_rank = m.get("avg_map_pack_rank", "N/A")
        citations = m.get("total_citations", 0)

        score = score_local_seo(gbp_score, citations)
        sec_cro = AuditSection(
            score=score,
            status="success",
            findings=[
                f"GBP Health Score: {gbp_score} / 100",
                f"Average Map Pack Rank: {map_rank}",
                f"Total Citations Tracked: {citations}"
            ],
            raw_data=bl_data
        )
    else:
        sec_cro = AuditSection(
            score=None,
            status="pending",
            findings=["No BrightLocal CSV found in input_csvs/"]
        )

    # --- AI Readiness & Generative Engine Optimization (Waikay CSV + Ping) ---
    sec_ai = live_results.get("ai_readiness", AuditSection())
    waikay_data = csv_data.get("waikay")
    if waikay_data and waikay_data.get("status") == "success":
        m = waikay_data.get("metrics", {})
        gen_score = m.get("generative_visibility_score", 0)
        mention_rate = m.get("brand_mention_rate", 0.0)
        platforms = m.get("top_ai_platforms", [])

        # Override or enrich findings with CSV data
        sec_ai.score = gen_score if gen_score > 0 else sec_ai.score
        sec_ai.findings.extend([
            f"Generative Visibility Score: {gen_score}/100",
            f"Brand Mention Rate: {mention_rate}%",
            f"Top AI Engines Tracked: {', '.join(str(p) for p in platforms[:3]) if platforms else 'None'}"
        ])
        sec_ai.raw_data["waikay_metrics"] = m

    # Combine into schema record
    record = ClientAuditRecord(
        client_domain=domain,
        security=live_results.get("security", AuditSection()),
        ai_readiness=sec_ai,
        website_health=live_results.get("website_health", AuditSection()),
        onpage_seo=live_results.get("onpage_seo", AuditSection()),
        gdpr_cookies=live_results.get("gdpr_cookies", AuditSection()),
        technical_seo=sec_technical,
        analytics_tracking=sec_analytics,
        content_strategy=sec_content,
        cro_ux=sec_cro
    )

    record.calculate_overall_score()
    return record
