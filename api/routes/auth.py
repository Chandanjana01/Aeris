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

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel, EmailStr

from api.db import get_db_connection
from api.limiter import limiter, verify_captcha

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
    captcha_token: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
    captcha_token: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    height: Optional[str] = "182 cm"
    weight: Optional[str] = "78 kg"
    sport: Optional[str] = "Track & Field / Basketball"
    position: Optional[str] = "Point Guard / Sprinter"
    baseline_knee: Optional[float] = 24.5
    baseline_spine: Optional[float] = 18.2
    baseline_hip: Optional[float] = 15.0
    baseline_fatigue: Optional[float] = 20.0
    injury_history: Optional[str] = "Left ACL Strain (2024)"


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    sport: Optional[str] = None
    position: Optional[str] = None
    baseline_knee: Optional[float] = None
    baseline_spine: Optional[float] = None
    baseline_hip: Optional[float] = None
    baseline_fatigue: Optional[float] = None
    injury_history: Optional[str] = None


class AuthResponse(BaseModel):
    status: str
    message: str
    access_token: str
    user: UserResponse


def _row_to_user(row) -> UserResponse:
    return UserResponse(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        role=row["role"],
        height=row["height"] if "height" in row.keys() else "182 cm",
        weight=row["weight"] if "weight" in row.keys() else "78 kg",
        sport=row["sport"] if "sport" in row.keys() else "Track & Field / Basketball",
        position=row["position"] if "position" in row.keys() else "Point Guard / Sprinter",
        baseline_knee=row["baseline_knee"] if "baseline_knee" in row.keys() else 24.5,
        baseline_spine=row["baseline_spine"] if "baseline_spine" in row.keys() else 18.2,
        baseline_hip=row["baseline_hip"] if "baseline_hip" in row.keys() else 15.0,
        baseline_fatigue=row["baseline_fatigue"] if "baseline_fatigue" in row.keys() else 20.0,
        injury_history=row["injury_history"] if "injury_history" in row.keys() else "Left ACL Strain (2024)"
    )


# ── Endpoints ──────────────────────────────────────────────────────────────
@router.post("/signup", response_model=AuthResponse, summary="Register a new user in SQLite")
@router.post("/api/auth/signup", response_model=AuthResponse, include_in_schema=False)
@limiter.limit("3/hour")
async def signup(request: Request, payload: SignupRequest):
    """
    Registers a new user account in SQLite `data/aeris.db`.
    - Rate limited to 3 requests / hour per IP (with CAPTCHA fallback).
    - Validates email uniqueness
    - Securely hashes password before saving
    """
    email = payload.email.strip().lower()
    full_name = payload.full_name.strip()
    password = payload.password.strip()

    # If CAPTCHA token provided, verify it
    if payload.captcha_token:
        is_captcha_valid = await verify_captcha(payload.captcha_token)
        if not is_captcha_valid:
            raise HTTPException(status_code=400, detail="CAPTCHA verification failed. Please try again.")

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

    cursor.execute("SELECT * FROM users WHERE id = ?", (new_user_id,))
    user_row = cursor.fetchone()
    conn.close()

    user_obj = _row_to_user(user_row)
    token = f"aeris_token_{new_user_id}_{secrets.token_hex(8)}"

    return AuthResponse(
        status="success",
        message="Account created successfully!",
        access_token=token,
        user=user_obj
    )


@router.post("/login", response_model=AuthResponse, summary="Authenticate user & verify password")
@router.post("/api/auth/login", response_model=AuthResponse, include_in_schema=False)
@limiter.limit("5/minute")
async def login(request: Request, payload: LoginRequest):
    """
    Authenticates a user against SQLite `data/aeris.db`.
    - Rate limited to 5 requests / minute per IP (with CAPTCHA fallback).
    """
    email = payload.email.strip().lower()
    password = payload.password.strip()

    # If CAPTCHA token provided, verify it
    if payload.captcha_token:
        is_captcha_valid = await verify_captcha(payload.captcha_token)
        if not is_captcha_valid:
            raise HTTPException(status_code=400, detail="CAPTCHA verification failed. Please try again.")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user_row["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    # Verify password hash
    if not verify_password(password, user_row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_obj = _row_to_user(user_row)
    token = f"aeris_token_{user_row['id']}_{secrets.token_hex(8)}"

    return AuthResponse(
        status="success",
        message="Login successful!",
        access_token=token,
        user=user_obj
    )



@router.get("/me", response_model=UserResponse, summary="Get current logged in user profile")
@router.get("/api/auth/me", response_model=UserResponse, include_in_schema=False)
@router.get("/user/profile", response_model=UserResponse, summary="Get athlete user profile")
@router.get("/api/user/profile", response_model=UserResponse, include_in_schema=False)
async def get_profile(user_id: Optional[int] = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        # Fallback to first available user or demo user
        cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1")
        user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        return UserResponse(
            id=1,
            full_name="Alex Morgan",
            email="alex.morgan@aeris.ai",
            role="athlete",
            height="182 cm",
            weight="78 kg",
            sport="Track & Field / Basketball",
            position="Point Guard / Sprinter",
            baseline_knee=24.5,
            baseline_spine=18.2,
            baseline_hip=15.0,
            baseline_fatigue=20.0,
            injury_history="Left ACL Strain (2024)"
        )

    return _row_to_user(user_row)


@router.put("/user/profile", response_model=UserResponse, summary="Update athlete user profile")
@router.put("/api/user/profile", response_model=UserResponse, include_in_schema=False)
async def update_profile(payload: ProfileUpdateRequest, user_id: Optional[int] = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()

    if not user_row:
        # Get first user ID if any
        cursor.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
        first_row = cursor.fetchone()
        if first_row:
            user_id = first_row["id"]

    updates = []
    params = []
    for field in ["full_name", "email", "role", "height", "weight", "sport", "position",
                  "baseline_knee", "baseline_spine", "baseline_hip", "baseline_fatigue", "injury_history"]:
        val = getattr(payload, field, None)
        if val is not None:
            updates.append(f"{field} = ?")
            params.append(val)

    if updates:
        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    updated_row = cursor.fetchone()
    conn.close()

    if not updated_row:
        raise HTTPException(status_code=404, detail="User not found")

    return _row_to_user(updated_row)

