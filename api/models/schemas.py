"""
Pydantic schemas for request/response validation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
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


class CorrectiveExercise(BaseModel):
    name: str
    target_area: str
    sets_reps: str
    description: str
    coaching_cue: str


class LLMRecommendations(BaseModel):
    engine: Optional[str] = None
    executive_summary: Optional[str] = None
    corrective_exercises: Optional[List[CorrectiveExercise]] = []
    posture_and_ergonomics: Optional[List[str]] = []
    recovery_protocol: Optional[List[str]] = []
    actionable_tips: Optional[List[str]] = []


class RiskReport(BaseModel):
    job_id: str
    video_name: str
    overall_risk: float
    risk_level: str
    body_part_risks: BodyPartRisks
    movement_scores: MovementScores
    alerts: List[str]
    recommendations: List[str]
    llm_recommendations: Optional[Dict[str, Any]] = None


class GenerateRecommendationsRequest(BaseModel):
    job_id: Optional[str] = None
    summary_override: Optional[Dict[str, Any]] = None


class GenerateRecommendationsResponse(BaseModel):
    success: bool
    engine: str
    llm_recommendations: Dict[str, Any]

