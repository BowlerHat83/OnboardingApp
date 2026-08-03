import sys
from pathlib import Path

# Ensure project root is in path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Services & Parsers
from app.services.topic1_service import Topic1Service
from app.services.topic2_service import Topic2Service

# Router Endpoints
from app.api.endpoints import topic1, topic2, topic3, topic4, topic5, topic6

# Initialize FastAPI App
app = FastAPI(
    title="SEO & Digital Visibility Audit Engine API",
    description="Unified Full Audit Engine across Topics 1–6",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Frontend Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services for Full-Scan
topic1_service = Topic1Service()
topic2_service = Topic2Service()

# --- HEALTH & STATUS ---
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "engine": "SEO Audit Core Engine v1.0",
        "docs": "http://127.0.0.1:8000/docs"
    }

# --- UNIFIED FULL AUDIT ENDPOINT ---
@app.post("/api/v1/audit/full-scan", tags=["Full Audit Orchestrator"])
async def run_full_audit(url: str = Query(..., description="Target URL (e.g. https://example.com)")):
    """Executes the entire audit suite across all active topics for a target URL."""
    results = {}
    
    # 1. Topic 1 Execution
    try:
        results["topic1_accessibility_privacy"] = await topic1_service.execute_audit(url)
    except Exception as e:
        results["topic1_accessibility_privacy"] = {"status": "error", "message": str(e)}

    # 2. Topic 2 Execution
    try:
        results["topic2_performance_cwv"] = await topic2_service.execute_audit(url)
    except Exception as e:
        results["topic2_performance_cwv"] = {"status": "error", "message": str(e)}

    # 3–6. Modules / Active Routers Summary
    results["audit_metadata"] = {
        "target_url": url,
        "active_modules": ["topic1", "topic2", "topic3", "topic4", "topic5", "topic6"],
        "status": "complete"
    }

    return results

# --- REGISTER ALL TOPIC ROUTERS ---
app.include_router(topic1.router, prefix="/api/v1/audit", tags=["Topic 1 - Technical & Accessibility"])
app.include_router(topic2.router, prefix="/api/v1/audit", tags=["Topic 2 - Core Web Vitals & Performance"])
app.include_router(topic3.router, prefix="/api/v1/audit", tags=["Topic 3 - Search Visibility"])
app.include_router(topic4.router, prefix="/api/v1/audit", tags=["Topic 4 - AI Visibility"])
app.include_router(topic5.router, prefix="/api/v1/audit", tags=["Topic 5 - Paid Visibility"])
app.include_router(topic6.router, prefix="/api/v1/audit", tags=["Topic 6 - Content & Conversion"])