"""
main.py — IntelliMind FastAPI Application
==========================================
Run with:  uvicorn main:app --reload --port 8000

Routes registered:
  /chat           → chat.py        (Karthik, Srikanth, Sarika, Harsha, Bhagya)
  /analyze-doc    → doc.py         (Srikanth — study document analyzer + /doc/chat)
  /resume/analyze → resume.py      (Sarika — ATS resume analyzer)
  /roadmap/*      → roadmap.py     (Bhagya — study plan generator)
  /progress/*     → analytics.py   (Karthik)
  /student/*      → student.py     (Harsha)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import chat, student, doc, debug, analytics
from app.routes import roadmap     # Bhagya's roadmap planner

# ── App ──
app = FastAPI(
    title="IntelliMind API",
    description="Backend for IntelliMind — AI Learning Intelligence",
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

# ── Routes ──
app.include_router(chat.router,      tags=["Chat"])
app.include_router(student.router,   tags=["Student"])
app.include_router(doc.router,       tags=["Document"])
app.include_router(roadmap.router)   # prefix="/roadmap" defined in the router
app.include_router(debug.router,     tags=["Debug"])
app.include_router(analytics.router, tags=["Analytics"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "IntelliMind API", "version": "1.0.0"}
