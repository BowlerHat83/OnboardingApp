from fastapi import APIRouter, UploadFile, File, HTTPException
from app.parsers.waikay_parser import parse_waikay_export
from app.services.topic4_service import Topic4Service

router = APIRouter()

@router.post("/topic4")
async def audit_topic4(file: UploadFile = File(...)):
    """
    Topic 4: AI Visibility & GEO Intelligence Audit Endpoint.
    Upload a Waikay CSV or JSON export to extract AI triggers, platform breakdowns, and competitor comparisons.
    """
    if not file.filename.endswith(('.csv', '.json', '.xlsx')):
        raise HTTPException(status_code=400, detail="File must be a CSV or JSON export from Waikay.")

    try:
        contents = await file.read()
        raw_data = parse_waikay_export(contents, filename=file.filename)
        
        service = Topic4Service(raw_data)
        report = service.process_intelligence()

        return {
            "topic": "Topic 4: AI Visibility & GEO Intelligence",
            "source_platform": "Waikay",
            "filename": file.filename,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Topic 4 audit: {str(e)}")