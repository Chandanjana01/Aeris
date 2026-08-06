"""
Thread-safe in-memory job store.

Tracks the status of each pipeline job using a simple dict protected
by a threading.Lock so concurrent requests don't corrupt state.

Structure of each job entry:
    {
        "status":     "queued" | "processing" | "done" | "failed",
        "video_name": str,   # used to locate risk_report.json on disk
        "error":      str | None
    }
"""

import threading
from typing import Any, Dict, Optional

_jobs: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def create_job(job_id: str, video_name: str) -> None:
    """Register a new job as 'queued'."""
    with _lock:
        _jobs[job_id] = {
            "status": "queued",
            "video_name": video_name,
            "error": None,
        }


def update_job(job_id: str, status: str, error: Optional[str] = None) -> None:
    """Update the status (and optionally error message) of an existing job."""
    with _lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = status
            if error is not None:
                _jobs[job_id]["error"] = error


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Return a copy of the job entry, or None if not found."""
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def list_jobs() -> Dict[str, Dict[str, Any]]:
    """Return a snapshot of all jobs (for debugging / admin)."""
    with _lock:
        return {jid: dict(info) for jid, info in _jobs.items()}
