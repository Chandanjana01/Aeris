"""
POST /analyze

Accepts a video file upload, saves it to disk, and kicks off the full
analysis pipeline in a background daemon thread.
Returns a job_id immediately so the client can poll for status.
"""

import shutil
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.job_store import create_job, update_job
from api.models.schemas import AnalyzeResponse, JobStatus

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def _run_pipeline(job_id: str, video_path: str, output_name: str) -> None:
    """
    Background worker: imports and runs the pipeline, then updates job status.
    Runs in a daemon thread so it doesn't block the API server.
    """
    # Import here (inside thread) to avoid any module-level side effects
    # at server startup time.
    from scripts.run_full_analysis import run_full_analysis

    update_job(job_id, "processing")
    try:
        result = run_full_analysis(video_path, output_name)
        if result is None:
            update_job(job_id, "failed", "Pipeline returned no result. Check server logs.")
        else:
            update_job(job_id, "done")
    except Exception as exc:
        update_job(job_id, "failed", str(exc))


@router.post("/analyze", response_model=AnalyzeResponse, summary="Upload a video and start analysis")
async def analyze_video(file: UploadFile = File(...)):
    """
    Upload a video file (.mp4 / .avi / .mov / .mkv / .wmv).

    The pipeline runs in the background. Use the returned **job_id** to:
    - Poll `GET /status/{job_id}` until status is `done` or `failed`
    - Fetch the result via `GET /report/{job_id}`
    """
    # --- Validate extension ---
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # --- Generate unique job ID ---
    job_id = str(uuid.uuid4())
    output_name = job_id  # output folder = job_id so it's always unique

    # --- Save uploaded video ---
    video_dir = Path("data/input_videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_dir / f"{job_id}{suffix}"

    try:
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {exc}")
    finally:
        await file.close()

    # --- Register job and fire background thread ---
    create_job(job_id, output_name)

    thread = threading.Thread(
        target=_run_pipeline,
        args=(job_id, str(video_path), output_name),
        daemon=True,
        name=f"pipeline-{job_id[:8]}",
    )
    thread.start()

    return AnalyzeResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message=f"Analysis queued. Poll GET /status/{job_id} to track progress.",
    )
