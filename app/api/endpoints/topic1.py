from fastapi import APIRouter, Query, HTTPException
from app.services.topic1_service import Topic1Service

router = APIRouter()
topic1_service = Topic1Service()

@router.post("/topic1", summary="Run Topic 1 Audit (Accessibility & DOM)")
async def run_topic1_audit(url: str = Query(..., description="Target URL (e.g. https://example.com)")):
    """Runs Topic 1 analysis for Accessibility (WCAG), DOM structure, and Privacy checks."""
    try:
        return await topic1_service.execute_audit(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic 1 execution failed: {str(e)}")