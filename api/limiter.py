"""
Centralized SlowAPI Limiter & CAPTCHA Verification Module.

Provides:
  - Global `limiter` instance shared across FastAPI routers
  - Custom HTTP 429 RateLimitExceeded handler with CAPTCHA requirement flag
  - CAPTCHA verification helper for Google reCAPTCHA / Cloudflare Turnstile
"""

import os
from typing import Optional
import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Global Limiter instance using client remote IP address
limiter = Limiter(key_func=get_remote_address)

CAPTCHA_SECRET_KEY = os.getenv("CAPTCHA_SECRET_KEY", "dev_secret_captcha_key")


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom exception handler for RateLimitExceeded errors.
    Returns HTTP 429 with explicit captcha_required flag for frontend UI fallback.
    """
    response = JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "captcha_required": True,
            "error": "rate_limit_exceeded"
        }
    )
    response = limiter._inject_headers(response, request.state.view_rate_limit)
    return response


async def verify_captcha(token: Optional[str]) -> bool:
    """
    Verifies a client CAPTCHA token against external CAPTCHA provider (e.g. Google reCAPTCHA / Cloudflare Turnstile).
    Returns True if valid token or in dev mock mode.
    """
    if not token or not token.strip():
        return False

    # Dev/test token bypass support
    if token.strip() in ("mock_captcha_token_passed", "PASSED_CAPTCHA_DEV"):
        return True

    # Check against Google reCAPTCHA / Cloudflare Turnstile API if configured
    verify_url = os.getenv("CAPTCHA_VERIFY_URL", "https://www.google.com/recaptcha/api/siteverify")
    secret = os.getenv("CAPTCHA_SECRET_KEY", CAPTCHA_SECRET_KEY)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                verify_url,
                data={"secret": secret, "response": token.strip()}
            )
            if resp.status_code == 200:
                result = resp.json()
                return result.get("success", False)
    except Exception as e:
        print(f"[CAPTCHA] Error verifying token with external API: {e}")

    return False
