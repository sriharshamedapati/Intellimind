"""
db.py — Database Clients (Supabase)
====================================
Provides two Supabase client instances:
1. supabase      → Points to the Data DB (Teammate Project)
2. auth_supabase → Points to the Auth DB (Primary Project)
"""
from app.config import settings

# ── 1. Main Data Client (Teammate) ──
supabase = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"[db] [OK] Data Supabase initialized: {settings.SUPABASE_URL}")
    except Exception as e:
        print(f"[db] [ERROR] Data Supabase failed: {e}")

# ── 2. Auth Verification Client (Primary) ──
auth_supabase = None
if settings.AUTH_SUPABASE_URL and settings.AUTH_SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        auth_supabase: Client = create_client(settings.AUTH_SUPABASE_URL, settings.AUTH_SUPABASE_KEY)
        print(f"[db] [OK] Auth Supabase initialized: {settings.AUTH_SUPABASE_URL}")
    except Exception as e:
        print(f"[db] [ERROR] Auth Supabase failed: {e}")
else:
    # Fallback to main if no separate auth configured
    auth_supabase = supabase
