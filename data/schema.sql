-- =======================================================
-- 1. SQLite Schema (User Authentication & Accounts)
-- File: data/aeris.db
-- =======================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'athlete', -- 'athlete', 'coach', 'admin'
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Query example to view users:
-- SELECT id, full_name, email, role, created_at FROM users;
-- =======================================================
-- 2. MongoDB Document Schema (For Future Reports Storage)
-- Database: aeris_db
-- Collection: risk_reports
-- =======================================================

/*
{
  "_id": ObjectId("..."),
  "job_id": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "user_email": "athlete@example.com",
  "video_name": "Sprint_Mechanics.mp4",
  "overall_risk": 47.5,
  "risk_level": "MODERATE",
  "body_part_risks": {
    "knee": 60.0,
    "hip": 30.0,
    "spine": 50.0,
    "fatigue": 0.0
  },
  "movement_scores": {
    "landing_quality": 63.4,
    "stability_score": 91.2,
    "symmetry_score": 96.1,
    "fatigue_score": 0.0
  },
  "alerts": [
    "High knee valgus detected."
  ],
  "recommendations": [
    "Strengthen hip abductors and improve knee alignment."
  ],
  "created_at": ISODate("2026-08-08T10:00:00Z")
}
*/
