"""
FastAPI application entry point.

Start the server:
    uvicorn api.main:app --reload

Interactive docs:
    http://127.0.0.1:8000/docs
"""

import os
import sys
from pathlib import Path

# ── Set working directory to project root ──────────────────────────────────
# The pipeline uses relative paths like "data/temp/frames/...".
# Changing CWD here (once, at startup) ensures those paths resolve correctly
# regardless of where the user launches uvicorn from.
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from api.routes import analyze, report, status

app = FastAPI(
    title="Ergonomic Risk Analysis API",
    description=(
        "Upload a video of a person moving and receive a full biomechanical "
        "risk assessment report. The pipeline uses Google MediaPipe to detect "
        "33 body landmarks and calculates joint angles, trunk lean, knee valgus, "
        "stability, and fatigue scores."
    ),
    version="1.0.0",
    contact={"name": "Risk Analyse Project"},
)

# Allow any frontend / Postman / mobile app to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ───────────────────────────────────────────────────────
app.include_router(analyze.router, tags=["1. Analysis"])
app.include_router(status.router,  tags=["2. Status"])
app.include_router(report.router,  tags=["3. Report"])

# ── Serve Frontend Dashboard ───────────────────────────────────────────────
frontend_path = PROJECT_ROOT / "frontend"
if frontend_path.exists():
    app.mount("/dashboard", StaticFiles(directory=str(frontend_path), html=True), name="dashboard")


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
async def root():
    return {
        "service": "Ergonomic Risk Analysis API",
        "status": "running",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "endpoints": {
            "upload_video":  "POST /analyze",
            "check_status":  "GET  /status/{job_id}",
            "fetch_report":  "GET  /report/{job_id}",
        },
    }
