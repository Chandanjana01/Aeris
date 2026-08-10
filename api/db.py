"""
Database connections for AERIS:
  - SQLite  → User accounts & authentication (data/aeris.db)
  - MongoDB → Risk analysis reports & biomechanical data (aeris_db.risk_reports)
"""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    PYMONGO_AVAILABLE = True
except ImportError:
    MongoClient = None
    Collection = Any = object
    PYMONGO_AVAILABLE = False

load_dotenv()

# ─── SQLite Config ────────────────────────────────────────────────────────────
DB_PATH = Path("data/aeris.db")

# ─── MongoDB Config ───────────────────────────────────────────────────────────
MONGO_URI     = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "aeris_db")

_mongo_client = None


def get_mongo_db():
    """
    Returns the aeris MongoDB database instance.
    Creates a singleton MongoClient connection on first call.
    """
    global _mongo_client
    if not PYMONGO_AVAILABLE:
        raise RuntimeError("pymongo package is not installed. Install via `pip install pymongo`.")

    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _mongo_client[MONGO_DB_NAME]


def get_reports_collection():
    """
    Returns the `risk_reports` collection from the aeris MongoDB database.
    Creates an index on job_id for fast lookups.
    """
    db = get_mongo_db()
    collection = db["risk_reports"]
    collection.create_index("job_id", unique=True)
    return collection



# ─── SQLite helpers ───────────────────────────────────────────────────────────

def get_db_connection():
    """
    Returns a sqlite3 connection with Row factory for dict-style access.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the SQLite `users` table if it does not exist, and migrates profile columns.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'athlete',
        is_active INTEGER DEFAULT 1,
        height TEXT DEFAULT '182 cm',
        weight TEXT DEFAULT '78 kg',
        sport TEXT DEFAULT 'Track & Field / Basketball',
        position TEXT DEFAULT 'Point Guard / Sprinter',
        baseline_knee REAL DEFAULT 24.5,
        baseline_spine REAL DEFAULT 18.2,
        baseline_hip REAL DEFAULT 15.0,
        baseline_fatigue REAL DEFAULT 20.0,
        injury_history TEXT DEFAULT 'Left ACL Strain (2024)',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure profile columns exist for legacy databases
    cursor.execute("PRAGMA table_info(users)")
    columns = [row["name"] for row in cursor.fetchall()]
    profile_columns = {
        "height": "TEXT DEFAULT '182 cm'",
        "weight": "TEXT DEFAULT '78 kg'",
        "sport": "TEXT DEFAULT 'Track & Field / Basketball'",
        "position": "TEXT DEFAULT 'Point Guard / Sprinter'",
        "baseline_knee": "REAL DEFAULT 24.5",
        "baseline_spine": "REAL DEFAULT 18.2",
        "baseline_hip": "REAL DEFAULT 15.0",
        "baseline_fatigue": "REAL DEFAULT 20.0",
        "injury_history": "TEXT DEFAULT 'Left ACL Strain (2024)'"
    }

    for col, col_def in profile_columns.items():
        if col not in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_def}")
            except Exception as exc:
                print(f"[SQLite DB] Note adding column {col}: {exc}")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    conn.commit()
    conn.close()

    print(f"[SQLite DB] Initialized user accounts database at: {DB_PATH.resolve()}")


# Auto-initialize SQLite on module load
init_db()

