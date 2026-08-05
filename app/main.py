import asyncio
import datetime
import traceback
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from app.collectors.a11y_auditor import ComprehensiveAuditor

app = FastAPI(
    title="Comprehensive Site Audit & Onboarding API",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auditor = ComprehensiveAuditor()

class AuditRequest(BaseModel):
    url: Optional[HttpUrl] = None
    target_url: Optional[HttpUrl] = None

    def get_url_str(self) -> str:
        target = self.url or self.target_url
        if not target:
            raise ValueError("Either 'url' or 'target_url' must be provided.")
        return str(target)

def calculate_grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"

@app.post("/api/v1/audit/run-full", tags=["Full Site Audit"])
async def run_full_audit(request: AuditRequest) -> Dict[str, Any]:
    try:
        target = request.get_url_str()
        print(f"\n--- STARTING AUDIT FOR: {target} ---")
        
        # Offload Playwright sync API execution to a separate worker thread
        a11y_results = await asyncio.to_thread(auditor.scan_page, target)
        print("--- AUDIT COMPLETED SUCCESSFULLY ---")

        wcag_data = a11y_results.get("accessibility_wcag22") or {}
        wcag_summary = wcag_data.get("summary") or {}
        wcag_violations = wcag_summary.get("total_violations", 0)
        
        gdpr_data = a11y_results.get("gdpr_compliance") or {
            "banner_detected": False,
            "pre_consent_cookie_count": 0,
            "tracking_cookie_count": 0,
            "is_compliant": False,
            "detected_script": "Custom / Unknown CMP",
            "summary_reason": "GDPR compliance check failed."
        }
        
        # Calculate scores
        t1_score = max(0.0, round(100.0 - (wcag_violations * 5.0), 2))
        gdpr_score = 100.0 if gdpr_data.get("is_compliant") else 50.0 if gdpr_data.get("banner_detected") else 0.0

        topic_analysis = {
            "topic_1a": {
                "title": "Technical & WCAG 2.2 Accessibility",
                "score": t1_score,
                "status": "PASS" if t1_score >= 80 else "NEEDS_IMPROVEMENT" if t1_score >= 60 else "CRITICAL_ACTION_NEEDED",
                "metrics": [
                    {"label": "WCAG Violations", "value": str(wcag_violations), "type": "warning" if wcag_violations > 0 else "good"},
                    {"label": "Critical Issues", "value": str(wcag_summary.get("critical", 0)), "type": "bad" if wcag_summary.get("critical", 0) > 0 else "good"}
                ]
            },
            "topic_1b": {
                "title": "GDPR & Cookie Compliance",
                "score": gdpr_score,
                "status": "PASS" if gdpr_data.get("is_compliant") else "CRITICAL_ACTION_NEEDED",
                "metrics": [
                    {"label": "Consent Banner", "value": "Detected" if gdpr_data.get("banner_detected") else "Missing", "type": "good" if gdpr_data.get("banner_detected") else "bad"},
                    {"label": "Pre-consent Cookies", "value": str(gdpr_data.get("tracking_cookie_count", 0)), "type": "good" if gdpr_data.get("tracking_cookie_count", 0) == 0 else "bad"},
                    {"label": "Detected CMP Script", "value": gdpr_data.get("detected_script", "Custom / Unknown CMP"), "type": "good"}
                ]
            }
        }

        total_score = sum(item["score"] for item in topic_analysis.values())
        overall_score = round(total_score / len(topic_analysis), 2)

        return {
            "audit_date": datetime.date.today().strftime("%B %d, %Y"),
            "target_url": target,
            "overall_score": overall_score,
            "overall_grade": calculate_grade(overall_score),
            "status": "Audit Complete",
            "topic_analysis": topic_analysis,
            "gdpr_compliance": gdpr_data,
            "top_priority_actions": [
                f"Accessibility: Fix {wcag_violations} WCAG violation(s) identified on the page.",
                "GDPR: Block pre-consent tracking cookies." if not gdpr_data.get("is_compliant") else "GDPR: Compliance verified."
            ],
            "a11y_report": a11y_results
        }

    except Exception as e:
        print("\n================ ERROR TRACEBACK ================")
        traceback.print_exc()
        print("=================================================\n")
        raise HTTPException(status_code=500, detail=f"Audit execution failed: {str(e)}")