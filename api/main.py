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

from api.routes import analyze, auth, progress, recommendations, report, status

app = FastAPI(
    title="AERIS Athlete Performance API",
    description=(
        "Unified Biomechanical Movement Intelligence & Ergonomic Risk Analysis API. "
        "Powered by Google MediaPipe keypoint tracking and Groq LLM physical therapy recommendation engine."
    ),
    version="2.0.0",
    contact={"name": "AERIS Movement Intelligence"},
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
app.include_router(auth.router,            tags=["0. Authentication"])
app.include_router(analyze.router,         tags=["1. Analysis"])
app.include_router(status.router,          tags=["2. Status"])
app.include_router(report.router,          tags=["3. Report"])
app.include_router(recommendations.router, tags=["4. AI Recommendations"])
app.include_router(progress.router,        tags=["5. Progress Tracking"])

# Also include with /api prefix for clean API route structure
app.include_router(auth.router,            prefix="/api", include_in_schema=False)
app.include_router(analyze.router,         prefix="/api", include_in_schema=False)
app.include_router(status.router,          prefix="/api", include_in_schema=False)
app.include_router(report.router,          prefix="/api", include_in_schema=False)
app.include_router(recommendations.router, prefix="/api", include_in_schema=False)
app.include_router(progress.router,        prefix="/api", include_in_schema=False)



# ── Serve Frontend Web App ───────────────────────────────────────────────
frontend_path = PROJECT_ROOT / "frontend"
if frontend_path.exists():
    app.mount("/dashboard", StaticFiles(directory=str(frontend_path), html=True), name="dashboard")
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/api/health", tags=["Health"], summary="API Health Check")
async def health_check():
    return {
        "service": "AERIS Athlete Performance API",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard"
    }

if frontend_path.exists():
    from fastapi.responses import FileResponse

    @app.get("/", tags=["Frontend"], summary="Serve AERIS Web App")
    async def serve_index():
        return FileResponse(str(frontend_path / "index.html"))

    @app.get("/{page_name}.html", tags=["Frontend"], include_in_schema=False)
    async def serve_page(page_name: str):
        page_file = frontend_path / f"{page_name}.html"
        if page_file.exists():
            return FileResponse(str(page_file))
        return FileResponse(str(frontend_path / "index.html"))

    @app.get("/aeris.css", include_in_schema=False)
    async def serve_css():
        return FileResponse(str(frontend_path / "aeris.css"))

    @app.get("/app.js", include_in_schema=False)
    async def serve_js():
        return FileResponse(str(frontend_path / "app.js"))

    @app.get("/logo.png", include_in_schema=False)
    async def serve_logo():
        return FileResponse(str(frontend_path / "logo.png"))



