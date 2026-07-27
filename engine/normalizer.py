import json
from datetime import datetime
from models.audit_schema import ClientAuditRecord, AuditSection
from pings.security_ping import audit_security
import pings.ai_readiness_ping as ai_ping
from pings.pagespeed_ping import audit_pagespeed
from pings.onpage_ping import audit_onpage
from pings.gdpr_cookie_ping import audit_gdpr_cookies
from concurrent.futures import ThreadPoolExecutor

run_ai_ping = getattr(ai_ping, 'audit_ai_readiness', getattr(ai_ping, 'check_ai_readiness', None))

def run_full_client_audit(domain: str) -> ClientAuditRecord:
    record = ClientAuditRecord(client_domain=domain)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        f_sec = executor.submit(audit_security, domain)
        f_ai = executor.submit(run_ai_ping, domain)
        f_speed = executor.submit(audit_pagespeed, domain)
        f_onpage = executor.submit(audit_onpage, domain)
        f_gdpr = executor.submit(audit_gdpr_cookies, domain)
        
        sec_res = f_sec.result()
        ai_res = f_ai.result()
        speed_res = f_speed.result()
        onpage_res = f_onpage.result()
        gdpr_res = f_gdpr.result()

    # Security
    record.security = AuditSection(
        score=sec_res.get("headers", {}).get("grade_score", 50),
        status="success",
        findings=[
            f"SSL Valid: {sec_res.get('ssl', {}).get('valid')} ({sec_res.get('ssl', {}).get('days_remaining')} days left)",
            f"HTTPS Enforced: {sec_res.get('protocol', {}).get('https_enforced')}"
        ],
        raw_data=sec_res
    )

    # AI Readiness
    ai_score_val = ai_res.get("ai_score", ai_res.get("score", 0))
    has_llms = ai_res.get("has_llms_txt", ai_res.get("llms_txt", {}).get("present", False))
    crawlers_ok = ai_res.get("ai_crawlers_allowed", True)
    record.ai_readiness = AuditSection(
        score=ai_score_val,
        status="success",
        findings=[
            f"llms.txt Present: {has_llms}",
            f"AI Crawlers Allowed: {crawlers_ok}"
        ],
        raw_data=ai_res
    )

    # Website Health
    record.website_health = AuditSection(
        score=speed_res.get("performance_score") or 50,
        status=speed_res.get("status", "pending"),
        findings=[
            f"Performance Score: {speed_res.get('performance_score')}",
            f"LCP: {speed_res.get('core_web_vitals', {}).get('lcp_ms')} ms"
        ],
        raw_data=speed_res
    )

    # On-Page SEO
    record.onpage_seo = AuditSection(
        score=onpage_res.get("score", 50),
        status="success",
        findings=[
            f"Word Count: {onpage_res.get('content', {}).get('word_count')}",
            f"H1 Count: {onpage_res.get('headings', {}).get('h1_count')}"
        ],
        raw_data=onpage_res
    )

    # GDPR
    record.gdpr_cookies = AuditSection(
        score=gdpr_res.get("compliance_score", 30),
        status="success",
        findings=[
            f"GDPR Risk Level: {gdpr_res.get('gdpr_risk_level')}",
            f"Unblocked Trackers: {', '.join(gdpr_res.get('unblocked_trackers_detected', []))}"
        ],
        raw_data=gdpr_res
    )

    record.calculate_overall_score()
    return record
