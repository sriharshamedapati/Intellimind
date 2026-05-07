"""
db.py — Database Clients (Supabase)
====================================
Single Supabase client instance, shared across the app.

FIXES:
- Wrapped client creation in try/except with clearer error messages
- Added fallback mode so the app can start even if Supabase is misconfigured
"""
from app.config import settings

supabase = None

if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    print("[db] ⚠️  SUPABASE_URL or SUPABASE_KEY missing from .env")
    print("[db]    Database features will be unavailable.")
else:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("[db] ✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"[db] ❌ Failed to initialize Supabase client: {type(e).__name__}: {e}")
        print("[db]    Database features will be unavailable.")
        supabase = None
