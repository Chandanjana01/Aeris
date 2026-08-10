"""
Progress Tracking API Route: GET /progress/summary
Provides historical trends, risk reduction metrics, and movement score tracking over time.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from api.routes.report import list_all_reports

router = APIRouter()


@router.get("/progress/summary", summary="Get athlete progress tracking summary")
@router.get("/api/progress/summary", include_in_schema=False)
async def get_progress_summary():
    """
    Computes aggregated progress statistics based on stored reports.
    """
    reports_data = await list_all_reports()
    raw_reports = reports_data.get("reports", [])

    total_sessions = len(raw_reports)
    if total_sessions == 0:
        # Default baseline simulation if no reports run yet
        return {
            "total_sessions": 12,
            "overall_risk_avg": 28.4,
            "risk_reduction_pct": -14.2,
            "fatigue_index_avg": 32.0,
            "trend_data": [
                {"date": "2026-07-15", "overall_risk": 42.0, "knee_risk": 48.0, "spine_risk": 35.0, "fatigue_risk": 40.0},
                {"date": "2026-07-22", "overall_risk": 38.5, "knee_risk": 42.0, "spine_risk": 31.0, "fatigue_risk": 36.0},
                {"date": "2026-07-29", "overall_risk": 34.0, "knee_risk": 36.0, "spine_risk": 28.0, "fatigue_risk": 32.0},
                {"date": "2026-08-05", "overall_risk": 28.4, "knee_risk": 24.5, "spine_risk": 22.0, "fatigue_risk": 26.0},
            ],
            "movement_scores": {
                "jump_score": 88,
                "landing_stability": 82,
                "gait_symmetry": 94,
                "sprint_mechanics": 89,
                "balance_control": 91,
                "mobility_score": 86
            },
            "recent_sessions": [
                {
                    "session_id": "demo-001",
                    "date": "2026-08-05",
                    "exercise": "Vertical Jump & Sprint",
                    "overall_risk": 28.4,
                    "risk_level": "LOW",
                    "primary_concern": "Knee Valgus on Landing"
                },
                {
                    "session_id": "demo-002",
                    "date": "2026-07-29",
                    "exercise": "Drop Jump Analysis",
                    "overall_risk": 34.0,
                    "risk_level": "MODERATE",
                    "primary_concern": "Asymmetric Impact Distribution"
                }
            ]
        }

    # Aggregate real reports
    total_risk = sum(r.get("overall_risk", 0) for r in raw_reports)
    avg_risk = round(total_risk / total_sessions, 1)

    # Sort chronologically (oldest first for trend calculation)
    chronological = sorted(raw_reports, key=lambda x: x.get("created_at", ""))

    first_risk = chronological[0].get("overall_risk", 35.0) if chronological else 35.0
    latest_risk = chronological[-1].get("overall_risk", 28.0) if chronological else 28.0
    reduction_pct = round(((latest_risk - first_risk) / max(first_risk, 1)) * 100, 1)

    trend_data = []
    for rep in chronological:
        bp = rep.get("body_part_risks", {})
        created = rep.get("created_at", "")[:10] if rep.get("created_at") else "Session"
        trend_data.append({
            "date": created,
            "overall_risk": rep.get("overall_risk", 0),
            "knee_risk": rep.get("knee_risk", bp.get("knee_risk", 0)),
            "spine_risk": rep.get("spine_risk", bp.get("spine_risk", 0)),
            "hip_risk": rep.get("hip_risk", bp.get("hip_risk", 0)),
            "fatigue_risk": rep.get("fatigue_risk", bp.get("fatigue_risk", 0)),
        })

    latest_rep = chronological[-1]
    mov_scores = latest_rep.get("movement_scores", {})

    return {
        "total_sessions": total_sessions,
        "overall_risk_avg": avg_risk,
        "risk_reduction_pct": reduction_pct,
        "fatigue_index_avg": round(sum(r.get("fatigue_risk", 0) for r in raw_reports) / max(total_sessions, 1), 1),
        "trend_data": trend_data,
        "movement_scores": {
            "jump_score": mov_scores.get("jump_score", 85),
            "landing_stability": mov_scores.get("landing_stability", 82),
            "gait_symmetry": mov_scores.get("gait_symmetry", 90),
            "sprint_mechanics": mov_scores.get("sprint_mechanics", 88),
            "balance_control": mov_scores.get("balance_control", 89),
            "mobility_score": mov_scores.get("mobility_score", 84)
        },
        "recent_sessions": raw_reports[:10]
    }
