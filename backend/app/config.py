"""
config.py — Centralized Configuration
=====================================
Single source of truth for all environment variables.
Loaded once at startup via python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        # ── Supabase ──
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
        
        # ── Auth Supabase (for JWT verification) ──
        self.AUTH_SUPABASE_URL: str = os.getenv("AUTH_SUPABASE_URL", "")
        self.AUTH_SUPABASE_KEY: str = os.getenv("AUTH_SUPABASE_KEY", "")

        # ── Gemini ──
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL: str = "gemini-2.0-flash"

        # ── Personalization ──
        self.MEMORY_LIMIT: int = int(os.getenv("MEMORY_LIMIT", "5"))

        # ── CORS ──
        # Allow common local dev ports + Vercel + custom env overrides
        env_origins = os.getenv("ALLOWED_ORIGINS", "")
        default_origins = [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5501",
            "http://localhost:5501",
            "http://127.0.0.1:5502",
            "http://localhost:5502",
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            "http://127.0.0.1:8080",
            "http://localhost:8080",
        ]

        if env_origins:
            custom = [o.strip() for o in env_origins.split(",") if o.strip()]
            # Merge: custom origins + defaults (no duplicates)
            merged = list(dict.fromkeys(custom + default_origins))
            self.ALLOWED_ORIGINS: list[str] = merged
        else:
            self.ALLOWED_ORIGINS: list[str] = default_origins

        # ── Validation ──
        self._validate()

    def _validate(self):
        if not self.GEMINI_API_KEY:
            print("[config] [WARN] GEMINI_API_KEY is missing - AI features will not work")

        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            print("[config] [WARN] Supabase credentials missing - DB features will not work")
        
        if self.GEMINI_API_KEY:
            print(f"[config] [OK] Gemini API key loaded (ends ...{self.GEMINI_API_KEY[-4:]})")
            print(f"[config] [OK] Model: {self.GEMINI_MODEL}")
        
        if self.SUPABASE_URL:
            print(f"[config] [OK] Supabase URL: {self.SUPABASE_URL}")

        print(f"[config] [OK] CORS origins: {len(self.ALLOWED_ORIGINS)} origins configured")


settings = Settings()