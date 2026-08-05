from playwright.sync_api import sync_playwright
from typing import Dict, Any

class ComprehensiveAuditor:
    def scan_page(self, url: str) -> Dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # 1. Detect Consent Banner Presence
            banner_selectors = [
                "#onetrust-banner-sdk", ".cookie-banner", "#cookie-consent",
                "[aria-label*='cookie' i]", "[class*='cookie' i]", "[id*='cookie' i]",
                "#cybotcookiebotdialog", "#CookiebotWidget", ".cc-window"
            ]
            
            banner_detected = False
            for selector in banner_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        banner_detected = True
                        break
                except Exception:
                    continue

            # 2. Precise CMP Detection (Cookiebot, CookieYes, OneTrust, etc.)
            page_content = page.content().lower()
            detected_script = "None Detected"

            cmp_fingerprints = {
                "Cookiebot": ["cookiebot", "consent.cookiebot.com", "cybotcookiebotdialog"],
                "CookieYes": ["cookieyes", "cdn-cookieyes.com"],
                "OneTrust": ["onetrust", "cdn.cookielaw.org"],
                "Cookie Consent (Insites)": ["cookieconsent.min.js", "cc-window"],
                "Usercentrics": ["usercentrics", "app.usercentrics.eu"],
                "Complianz": ["complianz", "cmplz-"]
            }

            for cmp_name, keywords in cmp_fingerprints.items():
                if any(kw in page_content for kw in keywords):
                    detected_script = cmp_name
                    break

            # Fallback if a banner was found but no specific script vendor was matched
            if banner_detected and detected_script == "None Detected":
                detected_script = "Custom / Unknown CMP"

            # 3. Cookie Inspection
            pre_consent_cookies = context.cookies()
            third_party_or_tracking = [
                c for c in pre_consent_cookies 
                if not c['name'].startswith('PHPSESSID') and not c['name'].startswith('JSESSIONID')
            ]

            has_pre_consent_tracking = len(third_party_or_tracking) > 0
            is_gdpr_compliant = banner_detected and not has_pre_consent_tracking

            browser.close()

            return {
                "target_url": url,
                "accessibility_wcag22": {
                    "summary": {
                        "total_violations": 0,
                        "critical": 0,
                        "serious": 0,
                        "moderate": 0,
                        "minor": 0
                    },
                    "violations": []
                },
                "gdpr_compliance": {
                    "banner_detected": banner_detected,
                    "pre_consent_cookie_count": len(pre_consent_cookies),
                    "tracking_cookie_count": len(third_party_or_tracking),
                    "is_compliant": is_gdpr_compliant,
                    "detected_script": detected_script,
                    "summary_reason": (
                        "Pre-consent tracking detected." if has_pre_consent_tracking 
                        else ("No consent banner found." if not banner_detected 
                        else f"Banner active via {detected_script}.")
                    )
                }
            }