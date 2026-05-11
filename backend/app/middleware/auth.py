"""
auth.py — JWT Authentication Middleware
========================================
Validates the Supabase JWT on every request except GET /.
If the token is missing or invalid, returns HTTP 401.
Injects the verified user_id into request.state for downstream routes.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.db import auth_supabase


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that extracts the Supabase JWT from the
    Authorization header and validates it on every request EXCEPT GET /.
    """

    # Routes that bypass authentication (method, path)
    EXEMPT_ROUTES = [
        ("GET", "/"),
        ("GET", "/docs"),
        ("GET", "/redoc"),
        ("GET", "/openapi.json"),
    ]

    async def dispatch(self, request: Request, call_next):
        method = request.method.upper()
        path = request.url.path.rstrip("/") or "/"

        # ── Skip exempt routes ──
        if (method, path) in self.EXEMPT_ROUTES:
            request.state.user_id = None
            return await call_next(request)

        # ── Skip OPTIONS (CORS preflight) ──
        if method == "OPTIONS":
            return await call_next(request)

        # ── Guard: auth client must be configured ──
        if not auth_supabase:
            print("[middleware/auth] [WARN] Auth Supabase not configured — skipping verification")
            request.state.user_id = None
            return await call_next(request)

        # ── Extract Authorization header ──
        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required. Please sign in again."},
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization format. Expected: Bearer <token>"},
            )

        token = parts[1]

        # ── Guard: token must not be "null" or "undefined" (JS edge case) ──
        if token in ("null", "undefined", ""):
            return JSONResponse(
                status_code=401,
                content={"detail": "Session expired. Please sign in again."},
            )

        # ── Verify with Supabase Auth ──
        try:
            res = auth_supabase.auth.get_user(token)

            if not res or not res.user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired session."},
                )

            # Inject verified user_id into request.state
            request.state.user_id = res.user.id
            print(f"[middleware/auth] [OK] Verified: {res.user.email}")

        except Exception as e:
            print(f"[middleware/auth] [ERROR] Verification failed: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed. Please sign in again."},
            )

        return await call_next(request)
