"""
Authentication Endpoints: POST /signup, POST /login, GET /me
Uses SQLite (data/aeris.db) for storing users with secure password hashing.
"""

import os
import sys
import hashlib
import secrets
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr

from api.db import get_db_connection

router = APIRouter()


# ── Password Hashing Helpers (PBKDF2 SHA-256 + Salt) ──────────────────────
def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a 16-byte random salt.
    Format stored in DB: salt_hex:hash_hex
    """
    salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a plain password against the stored salt_hex:hash_hex string.
    """
    try:
        salt_hex, pwd_hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return secrets.compare_digest(expected_hash.hex(), pwd_hash_hex)
    except Exception:
        return False


# ── Pydantic Request / Response Schemas ────────────────────────────────────
class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: Optional[str] = "athlete"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str


class AuthResponse(BaseModel):
    status: str
    message: str
    access_token: str
    user: UserResponse


# ── Endpoints ──────────────────────────────────────────────────────────────
@router.post("/signup", response_model=AuthResponse, summary="Register a new user in SQLite")
async def signup(payload: SignupRequest):
    """
    Registers a new user account in SQLite `data/aeris.db`.
    - Validates email uniqueness
    - Securely hashes password before saving
    """
    email = payload.email.strip().lower()
    full_name = payload.full_name.strip()
    password = payload.password.strip()

    if not email or not full_name or not password:
        raise HTTPException(status_code=400, detail="Full name, email, and password are required.")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    # Hash password & insert
    pwd_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (full_name, email, pwd_hash, payload.role or "athlete")
    )
    conn.commit()
    new_user_id = cursor.lastrowid

    cursor.execute("SELECT id, full_name, email, role FROM users WHERE id = ?", (new_user_id,))
    user_row = cursor.fetchone()
    conn.close()

    user_obj = UserResponse(
        id=user_row["id"],
        full_name=user_row["full_name"],
        email=user_row["email"],
        role=user_row["role"]
    )

    # Generate dummy bearer token (or JWT token)
    token = f"aeris_token_{new_user_id}_{secrets.token_hex(8)}"

    return AuthResponse(
        status="success",
        message="Account created successfully!",
        access_token=token,
        user=user_obj
    )


@router.post("/login", response_model=AuthResponse, summary="Authenticate user & verify password")
async def login(payload: LoginRequest):
    """
    Authenticates a user against SQLite `data/aeris.db`.
    - Retrieves user by email
    - Verifies hashed password
    - Returns access token & user profile
    """
    email = payload.email.strip().lower()
    password = payload.password.strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, full_name, email, password_hash, role, is_active FROM users WHERE LOWER(email) = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user_row["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    # Verify password hash
    if not verify_password(password, user_row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_obj = UserResponse(
        id=user_row["id"],
        full_name=user_row["full_name"],
        email=user_row["email"],
        role=user_row["role"]
    )

    token = f"aeris_token_{user_row['id']}_{secrets.token_hex(8)}"

    return AuthResponse(
        status="success",
        message="Login successful!",
        access_token=token,
        user=user_obj
    )
