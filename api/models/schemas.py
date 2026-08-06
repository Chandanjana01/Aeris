"""
Pydantic schemas for request/response validation.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


# ---------- /analyze ----------

class AnalyzeResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


# ---------- /status ----------

class StatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    video_name: Optional[str] = None
    error: Optional[str] = None


# ---------- /report ----------

class BodyPartRisks(BaseModel):
    knee: float
    hip: float
    spine: float
    fatigue: float


class MovementScores(BaseModel):
    landing_quality: float
    stability_score: float
    symmetry_score: float
    fatigue_score: float


class RiskReport(BaseModel):
    job_id: str
    video_name: str
    overall_risk: float
    risk_level: str
    body_part_risks: BodyPartRisks
    movement_scores: MovementScores
    alerts: List[str]
    recommendations: List[str]
