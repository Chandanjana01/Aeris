"""
Database Viewer Utility Script for AERIS SQLite Database.
Run: python scripts/view_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/aeris.db")


def view_users():
    if not DB_PATH.exists():
        print(f"[Error] Database file not found at {DB_PATH.resolve()}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, full_name, email, password_hash, role, is_active, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()

    print("==================================================================================================================================================")
    print(" AERIS SQLite User Accounts & Password Hashes (data/aeris.db)")
    print("==================================================================================================================================================")
    
    if not rows:
        print("No registered users found in database.")
        print("==================================================================================================================================================")
        return

    print(f"{'ID':<4} | {'Full Name':<18} | {'Email':<22} | {'Role':<8} | {'Password Hash (Salt:PBKDF2)':<45} | {'Created At':<19}")
    print("-" * 146)
    for row in rows:
        pwd_hash = row['password_hash']
        display_hash = pwd_hash[:42] + "..." if len(pwd_hash) > 45 else pwd_hash
        print(f"{row['id']:<4} | {row['full_name']:<18} | {row['email']:<22} | {row['role']:<8} | {display_hash:<45} | {row['created_at']:<19}")
    print("==================================================================================================================================================")


if __name__ == "__main__":
    view_users()
