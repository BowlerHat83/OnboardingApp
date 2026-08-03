import sys
from pathlib import Path

# Add project root directory to sys.path so 'app' imports resolve reliably
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Services & Parsers
from app.services.topic1_service import Topic1Service
from app.services.topic2_service import Topic2Service
from app.services.topic3_service import Topic3Service
from app.parsers.semrush import parse_semrush_excel

# Router Endpoints
from app.api.endpoints import topic4

# 1. Initialize Single FastAPI Instance
app = FastAPI(
    title="Comprehensive Site Auditor API",
    description="Backend service for Web Compliance, SEO, & Performance Auditing",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

topic1_service = Topic1Service()
topic2_service = Topic2Service()


# 2. Base & Health Endpoints
@app.get("/")
async def root():
    return {"message": "Audit Engine API is operational"}


# 3. Topic 1 & Topic 2 Crawl Endpoints
@app.post("/api/v1/audit/topic1")
async def run_topic1_audit(url: str):
    return await topic1_service.execute_audit(url)

@app.post("/api/v1/audit/topic2")
async def run_topic2_audit(url: str):
    return await topic2_service.execute_audit(url)

@app.post("/api/v1/audit/full-scan")
async def run_full_scan(url: str):
    t1_data = await topic1_service.execute_audit(url)
    t2_data = await topic2_service.execute_audit(url)
    return {
        "target_url": url,
        "topic_1_accessibility_privacy": t1_data,
        "topic_2_results": t2_data
    }


# 4. Topic 3 Endpoint (Keyword Intelligence & Search Visibility)
@app.post("/api/v1/audit/topic3")
async def run_topic3_audit(file: UploadFile = File(...)):
    """Accepts a Semrush/Ahrefs file and runs Topic 3 Keyword Intelligence analysis."""
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload .xlsx or .csv")

    try:
        contents = await file.read()
        parsed_sheets = parse_semrush_excel(contents)
        
        # Flatten sheet records into a single list of keywords
        all_records = []
        for sheet_name, rows in parsed_sheets.items():
            all_records.extend(rows)

        service = Topic3Service(all_records)
        report = service.process_intelligence()

        return {
            "topic": "Topic 3: Search Visibility & Keyword Intelligence",
            "filename": file.filename,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process keyword report: {str(e)}")


# 5. Register Topic 4 Router (AI Visibility & GEO)
app.include_router(topic4.router, prefix="/api/v1/audit", tags=["Topic 4 - AI Visibility"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import topic3, topic4, topic5  # Include topic5

app = FastAPI(title="Comprehensive Site Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Endpoints
app.include_router(topic3.router, prefix="/api/v1/audit", tags=["Topic 3 - Keyword Intelligence"])
app.include_router(topic4.router, prefix="/api/v1/audit", tags=["Topic 4 - AI Visibility"])
app.include_router(topic5.router, prefix="/api/v1/audit", tags=["Topic 5 - Paid Visibility"])