from fastapi import APIRouter, File, HTTPException, UploadFile
from app.parsers.semrush import parse_semrush_excel
from app.services.topic3_service import Topic3Service

router = APIRouter()


@router.post("/topic3")
async def audit_topic3(file: UploadFile = File(...)):
    """Topic 3: Keyword, Traffic & Search Visibility Audit Endpoint.

    Upload a Semrush/Ahrefs CSV or Excel export to compute keyword positions,
    search volume distributions, and ranking brackets.
    """
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a .csv or .xlsx export.",
        )

    try:
        contents = await file.read()

        # Parse sheets/records using our flexible parser
        parsed_sheets = parse_semrush_excel(contents)

        # Flatten records across sheets into a single list
        all_records = []
        for sheet_name, rows in parsed_sheets.items():
            all_records.extend(rows)

        # Calculate metrics using Topic3Service
        service = Topic3Service(all_records)
        report = service.process_intelligence()

        return {
            "topic": "Topic 3: Keyword, Traffic & Search Visibility",
            "filename": file.filename,
            "report": report,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Topic 3 audit: {str(e)}"
        )