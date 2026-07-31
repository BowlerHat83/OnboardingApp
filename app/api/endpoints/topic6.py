from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.topic6_service import Topic6Service

router = APIRouter()
service = Topic6Service()

@router.post("/topic6")
async def run_topic6_audit(
    target_url: str = Form(...),
    screaming_frog_csv: Optional[UploadFile] = File(None),
    content_gap_csv: Optional[UploadFile] = File(None)
):
    """
    Executes Topic 6 Audit:
    - Live scrapes target_url for CTAs, Form Structure, and Contact Links.
    - Processes manual Screaming Frog CSV (if uploaded).
    - Processes Ahrefs Content Gap CSV (if uploaded).
    """
    # 1. Scrape Live URL
    live_results = service.analyze_live_url(target_url)
    
    # 2. Screaming Frog Ingestion (Fallback mode check)
    sf_results = {}
    if screaming_frog_csv:
        content = await screaming_frog_csv.read()
        sf_results = service.parse_screaming_frog_csv(content)
    else:
        sf_results = {"status": "omitted", "warning": "No Screaming Frog CSV provided and local CLI skipped."}

    # 3. Content Gap Ingestion
    gap_results = []
    if content_gap_csv:
        gap_bytes = await content_gap_csv.read()
        gap_results = service.parse_content_gap_csv(gap_bytes)

    return {
        "topic": "Topic 6: Content, Architecture & Conversion Audit",
        "target_url": target_url,
        "live_site_analysis": live_results,
        "screaming_frog_metrics": sf_results,
        "content_gaps": gap_results
    }