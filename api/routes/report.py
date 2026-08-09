"""
Report routes — GET /report/{job_id} and GET /reports

Flow:
  - When a report is fetched for the first time it is upserted into MongoDB.
  - GET /reports reads directly from MongoDB (fast, no disk scanning).
  - Falls back to disk scan if MongoDB is unavailable.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from api.db import get_reports_collection
from api.job_store import get_job
from api.models.schemas import BodyPartRisks, MovementScores, RiskReport

router = APIRouter()


def _load_report_from_disk(job_id: str, video_name: str) -> dict:
    """Read risk_report.json from disk and return raw dict."""
    report_path = Path(f"data/output/{video_name}/risk_report.json")
    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report file not found on disk. The job may have been cleaned up.",
        )
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _upsert_to_mongo(job_id: str, data: dict) -> None:
    """
    Save / update the report document in MongoDB.
    Uses job_id as the unique key (upsert = insert or update).
    """
    try:
        collection = get_reports_collection()
        document = {
            "job_id": job_id,
            "video_name": data.get("video_name", job_id),
            "filename": data.get("video_name", job_id),
            "overall_risk": data.get("overall_risk", 0),
            "risk_level": data.get("risk_level", "UNKNOWN"),
            "body_part_risks": data.get("body_part_risks", {}),
            "movement_scores": data.get("movement_scores", {}),
            "knee_risk": data.get("body_part_risks", {}).get("knee_risk", 0),
            "spine_risk": data.get("body_part_risks", {}).get("spine_risk", 0),
            "hip_risk": data.get("body_part_risks", {}).get("hip_risk", 0),
            "fatigue_risk": data.get("body_part_risks", {}).get("fatigue_risk", 0),
            "alerts": data.get("alerts", []),
            "recommendations": data.get("recommendations", []),
            "llm_recommendations": data.get("llm_recommendations"),
            "created_at": data.get("created_at", datetime.now(timezone.utc).isoformat()),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        collection.update_one(
            {"job_id": job_id},
            {"$set": document},
            upsert=True,
        )
        print(f"[MongoDB] Report '{job_id}' upserted into aeris_db.risk_reports")
    except PyMongoError as exc:
        print(f"[MongoDB] Warning — could not save report '{job_id}': {exc}")


# ─── GET /report/{job_id} ─────────────────────────────────────────────────────

@router.get(
    "/report/{job_id}",
    response_model=RiskReport,
    summary="Retrieve the risk report for a completed analysis",
)
async def get_report(job_id: str):
    """
    Fetch the final risk assessment report for a job.

    1. Checks MongoDB first (fast path).
    2. Falls back to disk if not found in MongoDB.
    3. Upserts the report into MongoDB after reading from disk.
    """
    # ── Try MongoDB first ──────────────────────────────────────────────────────
    try:
        collection = get_reports_collection()
        doc = collection.find_one({"job_id": job_id})
        if doc:
            return RiskReport(
                job_id=job_id,
                video_name=doc.get("video_name", job_id),
                overall_risk=doc.get("overall_risk", 0),
                risk_level=doc.get("risk_level", "UNKNOWN"),
                body_part_risks=BodyPartRisks(**doc.get("body_part_risks", {})),
                movement_scores=MovementScores(**doc.get("movement_scores", {})),
                alerts=doc.get("alerts", []),
                recommendations=doc.get("recommendations", []),
                llm_recommendations=doc.get("llm_recommendations"),
            )
    except PyMongoError as exc:
        print(f"[MongoDB] Read failed, falling back to disk: {exc}")

    # ── Fallback: read from disk ───────────────────────────────────────────────
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

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

    data = _load_report_from_disk(job_id, job["video_name"])

    # Save to MongoDB for next time
    _upsert_to_mongo(job_id, data)

    return RiskReport(
        job_id=job_id,
        video_name=data["video_name"],
        overall_risk=data["overall_risk"],
        risk_level=data["risk_level"],
        body_part_risks=BodyPartRisks(**data["body_part_risks"]),
        movement_scores=MovementScores(**data["movement_scores"]),
        alerts=data.get("alerts", []),
        recommendations=data.get("recommendations", []),
        llm_recommendations=data.get("llm_recommendations"),
    )


# ─── GET /reports ─────────────────────────────────────────────────────────────

@router.get(
    "/reports",
    summary="List all historical risk assessment reports",
)
async def list_all_reports():
    """
    Returns all stored risk reports.

    Priority:
      1. Reads from MongoDB (aeris_db.risk_reports collection).
      2. Falls back to scanning data/output/ on disk if MongoDB unavailable.
         Also syncs any unsynced disk reports into MongoDB on fallback.
    """
    # ── Try MongoDB first ──────────────────────────────────────────────────────
    try:
        collection = get_reports_collection()
        docs = list(collection.find({}, {"_id": 0}).sort("created_at", -1))

        if docs:
            print(f"[MongoDB] Returning {len(docs)} reports from aeris_db.risk_reports")
            reports = []
            for doc in docs:
                try:
                    reports.append({
                        "job_id": doc.get("job_id", ""),
                        "filename": doc.get("filename", doc.get("video_name", "")),
                        "video_name": doc.get("video_name", ""),
                        "overall_risk": doc.get("overall_risk", 0),
                        "risk_level": doc.get("risk_level", "UNKNOWN"),
                        "knee_risk": doc.get("knee_risk", doc.get("body_part_risks", {}).get("knee_risk", 0)),
                        "spine_risk": doc.get("spine_risk", doc.get("body_part_risks", {}).get("spine_risk", 0)),
                        "hip_risk": doc.get("hip_risk", doc.get("body_part_risks", {}).get("hip_risk", 0)),
                        "fatigue_risk": doc.get("fatigue_risk", doc.get("body_part_risks", {}).get("fatigue_risk", 0)),
                        "body_part_risks": doc.get("body_part_risks", {}),
                        "movement_scores": doc.get("movement_scores", {}),
                        "alerts": doc.get("alerts", []),
                        "recommendations": doc.get("recommendations", []),
                        "llm_recommendations": doc.get("llm_recommendations"),
                        "created_at": doc.get("created_at"),
                    })
                except Exception as exc:
                    print(f"[MongoDB] Skipping malformed doc: {exc}")
            return {"reports": reports, "source": "mongodb", "count": len(reports)}

    except PyMongoError as exc:
        print(f"[MongoDB] Unavailable, falling back to disk scan: {exc}")

    # ── Fallback: scan data/output/ on disk ───────────────────────────────────
    output_dir = Path("data/output")
    reports = []

    if not output_dir.exists():
        return {"reports": [], "source": "disk", "count": 0}

    for folder in sorted(output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not folder.is_dir():
            continue
        report_file = folder / "risk_report.json"
        if not report_file.exists():
            continue
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            job_id = folder.name
            bp = data.get("body_part_risks", {})
            report_entry = {
                "job_id": job_id,
                "filename": data.get("video_name", folder.name),
                "video_name": data.get("video_name", folder.name),
                "overall_risk": data.get("overall_risk", 0),
                "risk_level": data.get("risk_level", "UNKNOWN"),
                "knee_risk": bp.get("knee_risk", 0),
                "spine_risk": bp.get("spine_risk", 0),
                "hip_risk": bp.get("hip_risk", 0),
                "fatigue_risk": bp.get("fatigue_risk", 0),
                "body_part_risks": bp,
                "movement_scores": data.get("movement_scores", {}),
                "alerts": data.get("alerts", []),
                "recommendations": data.get("recommendations", []),
                "llm_recommendations": data.get("llm_recommendations"),
                "created_at": data.get("created_at"),
            }
            reports.append(report_entry)

            # Sync to MongoDB while we're here
            _upsert_to_mongo(job_id, data)

        except Exception as exc:
            print(f"[Disk] Error loading report from {report_file}: {exc}")
            continue

    return {"reports": reports, "source": "disk_fallback", "count": len(reports)}
