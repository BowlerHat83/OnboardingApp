from fastapi import APIRouter, UploadFile, File, HTTPException
from app.parsers.spyfu_parser import parse_spyfu_export
from app.services.topic5_service import Topic5Service

router = APIRouter()


@router.post("/topic5")
async def audit_topic5(file: UploadFile = File(...)):
    """
    Topic 5: Paid Visibility & PPC Competitive Intelligence Endpoint.
    Accepts a SpyFu export (CSV, XLSX, or JSON) and returns:
    - Count of paid keywords
    - Top 25 keywords with search volume
    - Estimated Google Ads spend and average CPC
    - Paid visibility market share
    - Historic paid performance summary
    - Paid competitor comparisons
    """
    valid_extensions = ('.csv', '.xlsx', '.xls', '.json')
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400, 
            detail="File must be a CSV, XLSX, or JSON export from SpyFu."
        )

    try:
        contents = await file.read()
        raw_data = parse_spyfu_export(contents, filename=file.filename)
        
        service = Topic5Service(raw_data)
        report = service.process_intelligence()

        return {
            "topic": "Topic 5: Paid Visibility & PPC Competitive Intelligence",
            "source_platform": "SpyFu",
            "filename": file.filename,
            "report": report
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing Topic 5 audit: {str(e)}"
        )