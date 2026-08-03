import json
import asyncio
import urllib.request
from urllib.parse import urlparse
from typing import Dict, Any, List
from playwright.async_api import async_playwright

AXE_CORE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"


class ComprehensiveAuditor:
    def __init__(self):
        self._axe_script = None

    def _fetch_axe_core(self) -> str:
        """Downloads and caches axe-core JS into memory."""
        if not self._axe_script:
            req = urllib.request.Request(AXE_CORE_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                self._axe_script = response.read().decode("utf-8")
        return self._axe_script

    async def scan_page(
        self, 
        url: str, 
        tags: List[str] = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
    ) -> Dict[str, Any]:
        """
        Runs a single-pass headless audit capturing:
        1. WCAG 2.2 AA Accessibility Violations (axe-core)
        2. First-Party vs. Third-Party Cookie Dump (Pre-consent GDPR)
        3. CMP Consent Banner Detection (OneTrust, Cookiebot, etc.)
        """
        axe_js = self._fetch_axe_core()
        domain = urlparse(url).netloc.replace("www.", "")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                print(f" Navigating to {url}...")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector("body", timeout=10000)

                # --- 1. COOKIE AUDIT (Pre-Consent / Initial Load) ---
                raw_cookies = await context.cookies()
                cookie_audit = self._audit_cookies(raw_cookies, domain)

                # --- 2. CMP / CONSENT BANNER DETECTION ---
                cmp_detected = await page.evaluate("""() => {
                    const html = document.documentElement.outerHTML.toLowerCase();
                    const scripts = Array.from(document.scripts).map(s => s.src.toLowerCase());
                    
                    if (scripts.some(s => s.includes('onetrust')) || html.includes('onetrust')) return 'OneTrust';
                    if (scripts.some(s => s.includes('cookiebot')) || html.includes('cookiebot')) return 'Cookiebot';
                    if (scripts.some(s => s.includes('usercentrics')) || html.includes('usercentrics')) return 'Usercentrics';
                    if (scripts.some(s => s.includes('osano')) || html.includes('osano')) return 'Osano';
                    if (scripts.some(s => s.includes('complianz')) || html.includes('complianz')) return 'Complianz';
                    if (scripts.some(s => s.includes('cookie-law-info')) || html.includes('cli-modal')) return 'Cookie Law Info';
                    
                    return null;
                }""")

                # --- 3. ACCESSIBILITY AUDIT (axe-core) ---
                print(" Injecting axe-core engine into DOM...")
                await page.evaluate(axe_js)
                axe_options = {"runOnly": {"type": "tag", "values": tags}}

                print(" Running WCAG 2.2 AA audit...")
                raw_axe_results = await page.evaluate(f"axe.run({json.dumps(axe_options)})")
                a11y_summary = self._format_a11y_report(url, raw_axe_results)

                # --- UNIFIED COMPLIANCE OUTPUT ---
                return {
                    "url": url,
                    "timestamp": raw_axe_results.get("timestamp"),
                    "accessibility_wcag22": a11y_summary,
                    "privacy_and_cookies": {
                        "cmp_detected": cmp_detected,
                        "cookie_summary": cookie_audit["summary"],
                        "all_cookies": cookie_audit["cookies_detail"]
                    }
                }

            finally:
                await browser.close()

    def _audit_cookies(self, cookies: List[Dict[str, Any]], root_domain: str) -> Dict[str, Any]:
        """Categorizes cookies into First-Party vs Third-Party and flags potential pre-consent risks."""
        first_party = []
        third_party = []
        known_tracking_prefixes = ['_ga', '_fbp', '_gid', '_gat', 'clsk', '_uetsid', '_uetvid']

        flagged_pre_consent = []

        for c in cookies:
            cookie_domain = c.get("domain", "").lstrip(".").replace("www.", "")
            cookie_info = {
                "name": c.get("name"),
                "domain": c.get("domain"),
                "path": c.get("path"),
                "expires": c.get("expires"),
                "http_only": c.get("httpOnly"),
                "secure": c.get("secure"),
                "same_site": c.get("sameSite")
            }

            # Check if domain matches root
            if root_domain in cookie_domain or cookie_domain in root_domain:
                first_party.append(cookie_info)
            else:
                third_party.append(cookie_info)

            # Check for common tracking cookies set prior to user consent
            if any(c.get("name", "").startswith(prefix) for prefix in known_tracking_prefixes):
                flagged_pre_consent.append(c.get("name"))

        return {
            "summary": {
                "total_cookies": len(cookies),
                "first_party_count": len(first_party),
                "third_party_count": len(third_party),
                "pre_consent_tracking_flag": len(flagged_pre_consent) > 0,
                "flagged_tracking_cookies": flagged_pre_consent
            },
            "cookies_detail": {
                "first_party": first_party,
                "third_party": third_party
            }
        }

    def _format_a11y_report(self, url: str, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Formats raw axe-core findings."""
        violations = raw_results.get("violations", [])
        impact_counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
        formatted_violations = []

        for v in violations:
            impact = v.get("impact", "minor")
            if impact in impact_counts:
                impact_counts[impact] += 1

            nodes_affected = []
            for node in v.get("nodes", []):
                nodes_affected.append({
                    "target": node.get("target", []),
                    "html_snippet": node.get("html", ""),
                    "failure_summary": node.get("failureSummary", "")
                })

            formatted_violations.append({
                "rule_id": v.get("id"),
                "impact": impact,
                "description": v.get("description"),
                "help_url": v.get("helpUrl"),
                "nodes_count": len(nodes_affected),
                "nodes": nodes_affected[:3]  # Capture first 3 node samples
            })

        return {
            "summary": {
                "total_violations": len(violations),
                "passes_count": len(raw_results.get("passes", [])),
                "incomplete_count": len(raw_results.get("incomplete", [])),
                "impact_breakdown": impact_counts
            },
            "violations": formatted_violations
        }


if __name__ == "__main__":
    async def main():
        auditor = ComprehensiveAuditor()
        target_url = "https://www.bowlerhat.co.uk"
        
        report = await auditor.scan_page(target_url)
        
        print("\n" + "="*50)
        print("AUDIT SUMMARY COMPLETE")
        print("="*50)
        print(json.dumps({
            "accessibility_summary": report["accessibility_wcag22"]["summary"],
            "privacy_and_cookies_summary": report["privacy_and_cookies"]["cookie_summary"],
            "cmp_detected": report["privacy_and_cookies"]["cmp_detected"]
        }, indent=2))

        # Save full detailed output
        with open("full_compliance_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print("\n Full detailed report saved to 'full_compliance_report.json'")

    asyncio.run(main())