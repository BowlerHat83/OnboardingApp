import requests
from typing import Dict, Any

def audit_robots_txt(domain: str) -> Dict[str, Any]:
    """
    Checks robots.txt presence, sitemap links, and global site block directives.
    """
    clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
    url = f"https://{clean_domain}/robots.txt"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            content = response.text.lower()
            has_sitemap = "sitemap:" in content
            # Checks if robots.txt blocks all crawlers without allow exceptions
            is_blocking_site = "disallow: /" in content and "allow:" not in content
            
            return {
                "exists": True,
                "has_sitemap_link": has_sitemap,
                "is_blocking_site": is_blocking_site,
                "status_code": 200
            }
        
        return {
            "exists": False,
            "has_sitemap_link": False,
            "is_blocking_site": False,
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "exists": False,
            "has_sitemap_link": False,
            "is_blocking_site": False,
            "error": str(e)
        }
