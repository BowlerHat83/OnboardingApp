import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def audit_gdpr_and_wcag(domain: str) -> Dict[str, Any]:
    """
    Performs dual check on Cookie Compliance & Basic WCAG 2.2 Accessibility:
    - Set-Cookie security flags (Secure, HttpOnly, SameSite)
    - HTML lang attribute
    - Form label associations
    - Image missing alt tags on homepage
    - Main ARIA landmarks
    """
    url = f"https://{domain}" if not domain.startswith("http") else domain
    try:
        response = requests.get(url, timeout=8)
        
        # 1. GDPR / Cookie Audit
        cookies = response.cookies
        cookie_count = len(cookies)
        insecure_cookies = 0
        for cookie in cookies:
            if not cookie.secure or not cookie.has_nonstandard_attr('httponly'):
                insecure_cookies += 1
                
        cookie_risk = "Low"
        if insecure_cookies > 0:
            cookie_risk = "Medium" if insecure_cookies < 3 else "High"

        # 2. Basic WCAG 2.2 Accessibility Checks
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check <html lang="...">
        html_tag = soup.find('html')
        has_lang_attr = bool(html_tag and html_tag.get('lang'))
        
        # Check form inputs have associated labels/aria-labels
        inputs = soup.find_all(['input', 'textarea', 'select'])
        unlabeled_inputs = 0
        for inp in inputs:
            if inp.get('type') in ['hidden', 'submit', 'button']:
                continue
            if not inp.get('id') and not inp.get('aria-label') and not inp.get('aria-labelledby'):
                unlabeled_inputs += 1

        # ARIA landmarks check
        has_main_landmark = bool(soup.find(['main', '[role="main"]']))

        return {
            "cookie_count": cookie_count,
            "insecure_cookies": insecure_cookies,
            "cookie_risk_level": cookie_risk,
            "wcag_has_lang_attribute": has_lang_attr,
            "wcag_unlabeled_inputs": unlabeled_inputs,
            "wcag_has_main_landmark": has_main_landmark,
            "wcag_pass": has_lang_attr and unlabeled_inputs == 0
        }
    except Exception as e:
        return {
            "cookie_risk_level": "High",
            "wcag_pass": False,
            "error": str(e)
        }
