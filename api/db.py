"""
SQLite User Account Database Connection & Initializer.

Stores user registration credentials and login details in data/aeris.db.
(Analysis reports & video metadata will be stored in MongoDB).
"""

import sqlite3
from pathlib import Path

# Path to local SQLite database file
DB_PATH = Path("data/aeris.db")


def get_db_connection():
    """
    Returns a connected sqlite3 database connection object configured
    with Row factory so columns can be accessed like dictionaries.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes SQLite `users` table if it does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table for Login / Signup Credentials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'athlete',
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

    conn.commit()
    conn.close()

    print(f"[SQLite DB] Initialized user accounts database at: {DB_PATH.resolve()}")


# Auto-initialize database on module load
init_db()
