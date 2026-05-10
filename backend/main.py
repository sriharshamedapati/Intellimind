"""
main.py — INTELLMIND FastAPI Application
==========================================
Run with:  uvicorn main:app --reload --port 8000

Routes registered:
  /chat           → chat.py
  /analyze-doc    → doc.py
  /roadmap/*      → roadmap.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import chat, doc
from app.routes import roadmap
from app.middleware.auth import JWTAuthMiddleware

# ── App ──
app = FastAPI(
    title="INTELLMIND API",
    description="Backend for INTELLMIND — AI Learning Intelligence",
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth Middleware ──
app.add_middleware(JWTAuthMiddleware)

# ── Routes ──
app.include_router(chat.router,      tags=["Chat"])
app.include_router(doc.router,       tags=["Document"])
app.include_router(roadmap.router)   # prefix="/roadmap" defined in the router


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "INTELLMIND API", "version": "1.0.0"}
