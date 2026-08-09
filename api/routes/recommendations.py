"""
POST /recommendations/generate

Interactive Groq LLM Recommendation endpoint.
Allows generating AI physical therapy & ergonomic advice on-demand.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from api.models.schemas import GenerateRecommendationsRequest, GenerateRecommendationsResponse
from src.risk_assessment.recommendations import generate_llm_recommendations, generate_recommendations

router = APIRouter()


@router.post(
    "/recommendations/generate",
    response_model=GenerateRecommendationsResponse,
    summary="Generate Groq LLM-powered ergonomic recommendations on demand",
)
async def generate_ai_recommendations(req: GenerateRecommendationsRequest):
    """
    Generate or re-generate custom AI physical therapy recommendations using Groq LLM.
    
    Can accept a `job_id` to load existing report data or a `summary_override` payload.
    """
    summary = {}
    alerts = []

    if req.job_id:
        output_dir = Path("data/output")
        report_file = output_dir / req.job_id / "risk_report.json"
        
        # Search by folder name or video name
        if not report_file.exists():
            for folder in output_dir.iterdir():
                if folder.is_dir():
                    candidate = folder / "risk_report.json"
                    if candidate.exists():
                        try:
                            with open(candidate, "r", encoding="utf-8") as f:
                                r_data = json.load(f)
                            if r_data.get("video_name") == req.job_id or folder.name == req.job_id:
                                report_file = candidate
                                break
                        except Exception:
                            continue

        if not report_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report file for job/video '{req.job_id}' not found.",
            )

        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary = {
            "video_name": data.get("video_name", req.job_id),
            "overall_risk": data.get("overall_risk", 0.0),
            "risk_level": data.get("risk_level", "LOW"),
            "knee_risk": data.get("body_part_risks", {}).get("knee", 0.0),
            "hip_risk": data.get("body_part_risks", {}).get("hip", 0.0),
            "spine_risk": data.get("body_part_risks", {}).get("spine", 0.0),
            "fatigue_risk": data.get("body_part_risks", {}).get("fatigue", 0.0),
            "landing_quality": data.get("movement_scores", {}).get("landing_quality", 100.0),
            "stability_score": data.get("movement_scores", {}).get("stability_score", 100.0),
            "avg_symmetry": data.get("movement_scores", {}).get("symmetry_score", 100.0),
            "fatigue_score": data.get("movement_scores", {}).get("fatigue_score", 0.0),
            "peak_knee_valgus": data.get("peak_knee_valgus", 0.0),
            "peak_trunk_lean": data.get("peak_trunk_lean", 0.0),
        }
        alerts = data.get("alerts", [])

    if req.summary_override:
        summary.update(req.summary_override)
        if not alerts:
            alerts, _ = generate_recommendations(summary)

    if not summary:
        raise HTTPException(
            status_code=400,
            detail="Either 'job_id' or 'summary_override' must be provided.",
        )

    llm_recs = generate_llm_recommendations(summary, alerts)
    engine_name = llm_recs.get("engine", "Groq LLM")

    # If linked to a job_id, optionally update the stored risk_report.json
    if req.job_id and 'report_file' in locals() and report_file.exists():
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                rep_data = json.load(f)
            rep_data["llm_recommendations"] = llm_recs
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(rep_data, f, indent=4)
        except Exception as exc:
            print(f"Warning: Could not update risk_report.json with new LLM recommendations: {exc}")

    return GenerateRecommendationsResponse(
        success=True,
        engine=engine_name,
        llm_recommendations=llm_recs,
    )
