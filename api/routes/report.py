"""
GET /report/{job_id}

Returns the full risk_report.json content for a completed job.
This is the data that should be stored in the database.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.job_store import get_job
from api.models.schemas import BodyPartRisks, MovementScores, RiskReport

router = APIRouter()


@router.get(
    "/report/{job_id}",
    response_model=RiskReport,
    summary="Retrieve the risk report for a completed analysis",
)
async def get_report(job_id: str):
    """
    Fetch the final risk assessment report.

    Only call this after `GET /status/{job_id}` returns `done`.

    **Response contains:**
    - `overall_risk` — composite score 0–100
    - `risk_level` — LOW / MODERATE / HIGH / VERY HIGH
    - `body_part_risks` — individual scores for knee, hip, spine, fatigue
    - `movement_scores` — landing quality, stability, symmetry, fatigue
    - `alerts` — specific risk flags detected
    - `recommendations` — actionable improvement tips
    """
    job = get_job(job_id)

    # --- Job existence check ---
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    # --- Status checks ---
    status = job["status"]
    if status in ("queued", "processing"):
        raise HTTPException(
            status_code=202,
            detail="Analysis is still in progress. Poll GET /status/{job_id} and retry when done.",
        )
    if status == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {job.get('error', 'Unknown error')}",
        )

    # --- Read risk_report.json from disk ---
    report_path = Path(f"data/output/{job['video_name']}/risk_report.json")
    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report file not found on disk. The job may have been cleaned up.",
        )

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return RiskReport(
        job_id=job_id,
        video_name=data["video_name"],
        overall_risk=data["overall_risk"],
        risk_level=data["risk_level"],
        body_part_risks=BodyPartRisks(**data["body_part_risks"]),
        movement_scores=MovementScores(**data["movement_scores"]),
        alerts=data["alerts"],
        recommendations=data["recommendations"],
    )
