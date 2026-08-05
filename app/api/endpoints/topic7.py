from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.topic7_service import Topic7Service

router = APIRouter(prefix="/topic7", tags=["Topic 7 - Local SEO & GBP"])
service = Topic7Service()


@router.post("/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_topic7(payload: Dict[str, Any]):
    """Evaluates Topic 7 metrics directly from a JSON body."""
    try:
        return service.evaluate_payload(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to evaluate Topic 7: {str(e)}"
        )


@router.post("/upload-csv", status_code=status.HTTP_200_OK)
async def upload_brightlocal_csv(file: UploadFile = File(...)):
    """Uploads and evaluates a BrightLocal CSV export."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .csv file."
        )

    try:
        csv_bytes = await file.read()
        return service.process_csv_bytes(csv_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing CSV: {str(e)}"
        )
