"""
auth.py — Authentication Dependencies
=====================================
Verifies Supabase JWT tokens in the Authorization header.
Uses the AUTH Supabase client (Primary Project) for token verification.
The Data Supabase (Teammate Project) is used elsewhere for queries.
"""
from fastapi import Header, HTTPException
from app.db import auth_supabase


async def get_current_user(authorization: str = Header(None)):
    """
    FastAPI dependency — verifies the Supabase JWT token.
    Expects header: Authorization: Bearer <token>
    Returns the authenticated user object on success.
    """
    # ── Guard: auth client must be configured ──
    if not auth_supabase:
        # If auth is not configured, log a warning but let the request through
        # This prevents the app from breaking if AUTH env vars are missing
        print("[auth] ⚠️  Auth Supabase not configured — skipping verification")
        return None

    # ── Guard: header must be present ──
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in again."
        )

    # ── Extract Bearer token ──
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = parts[1]

    # ── Guard: token must not be "null" or "undefined" (JS edge case) ──
    if token in ("null", "undefined", ""):
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please sign in again."
        )

    # ── Verify with Supabase Auth ──
    try:
        res = auth_supabase.auth.get_user(token)

        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        print(f"[auth] ✅ Verified user: {res.user.email}")
        return res.user

    except HTTPException:
        raise  # Re-raise our own HTTPExceptions
    except Exception as e:
        print(f"[auth] ❌ Verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Please sign in again."
        )


def verify_student_roll(requested_roll: str, user):
    """
    Verify that the authenticated user is accessing their own data.
    If auth is disabled (user is None), skip the check.
    """
    # Skip if auth is not configured or user is None
    if user is None:
        return True

    # Skip if user has no email (shouldn't happen, but defensive)
    if not hasattr(user, 'email') or not user.email:
        return True

    # Compare: email prefix (before @) vs requested roll
    email_roll = user.email.split('@')[0].upper().strip()
    requested  = requested_roll.upper().strip()

    if email_roll != requested:
        print(f"[auth] 🚫 Roll mismatch: token={email_roll}, requested={requested}")
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this student's data."
        )

    return True
