"""
GET /status/{job_id}

Returns the current status of a pipeline job:
  - queued      : received, not yet started
  - processing  : pipeline is running
  - done        : risk_report.json is ready
  - failed      : pipeline crashed (error message included)
"""

from fastapi import APIRouter, HTTPException

from api.job_store import get_job
from api.models.schemas import JobStatus, StatusResponse

router = APIRouter()


@router.get(
    "/status/{job_id}",
    response_model=StatusResponse,
    summary="Check the status of an analysis job",
)
async def get_status(job_id: str):
    """
    Poll this endpoint after calling `POST /analyze`.

    **Status values:**
    | Status | Meaning |
    |---|---|
    | `queued` | Job accepted, pipeline not started yet |
    | `processing` | Pipeline is actively running |
    | `done` | Analysis complete — call `GET /report/{job_id}` |
    | `failed` | Pipeline failed — see `error` field for details |
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return StatusResponse(
        job_id=job_id,
        status=JobStatus(job["status"]),
        video_name=job.get("video_name"),
        error=job.get("error"),
    )
