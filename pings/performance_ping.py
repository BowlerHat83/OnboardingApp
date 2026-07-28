import requests
import time
from typing import Dict, Any

def audit_performance(domain: str) -> Dict[str, Any]:
    """
    Evaluates site speed metrics:
    - Time To First Byte (TTFB) < 1.0s target
    - Page payload size < 3.0MB target
    - Estimated 5G load time < 2.5s target
    """
    url = f"https://{domain}" if not domain.startswith("http") else domain
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        
        # Calculate TTFB in seconds
        ttfb = round(response.elapsed.total_seconds(), 3)
        
        # Calculate page payload size in Megabytes
        content_bytes = len(response.content)
        payload_mb = round(content_bytes / (1024 * 1024), 2)
        
        # Estimated 5G Load Time (typical 5G download ~50 Mbps = 6.25 MB/s)
        estimated_5g_load_time = round(ttfb + (payload_mb / 6.25), 2)
        
        return {
            "ttfb_seconds": ttfb,
            "ttfb_passed": ttfb <= 1.0,
            "payload_mb": payload_mb,
            "payload_passed": payload_mb <= 3.0,
            "estimated_5g_load_time": estimated_5g_load_time,
            "5g_passed": estimated_5g_load_time <= 2.5,
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "ttfb_seconds": 0.0,
            "ttfb_passed": False,
            "payload_mb": 0.0,
            "payload_passed": False,
            "estimated_5g_load_time": 0.0,
            "5g_passed": False,
            "error": str(e)
        }
