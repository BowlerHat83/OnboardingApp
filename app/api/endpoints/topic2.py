from fastapi import APIRouter, Query, HTTPException
from app.services.topic2_service import Topic2Service

router = APIRouter()
topic2_service = Topic2Service()

@router.post("/topic2", summary="Run Topic 2 Audit (Performance & Core Web Vitals)")
async def run_topic2_audit(url: str = Query(..., description="Target URL (e.g. https://example.com)")):
    """Runs Topic 2 analysis for Core Web Vitals, PageSpeed, and Screaming Frog audit data."""
    try:
        return await topic2_service.execute_audit(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic 2 execution failed: {str(e)}")