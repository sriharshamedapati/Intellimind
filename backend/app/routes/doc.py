"""
doc.py — Document Analyser Route (STUDY DOCUMENTS)
====================================================
POST /analyze-doc  → Upload study material, extract text, get AI summary
                     Returns session_id for follow-up chat
POST /doc/chat     → Ask questions about the uploaded document
                     Uses session_id to retrieve stored document text

Owner: Srikanth / Karthik (integration)
"""

import io
import uuid
import time
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.services.gemini import call_gemini_rest, extract_text

router = APIRouter()

# ─── In-Memory Session Store ──────────────────────────────────────────────────
# { session_id: { "text": str, "filename": str, "created_at": datetime } }
_session_store: dict = {}
SESSION_EXPIRY_SECONDS = 3600  # 1 hour
MAX_SESSIONS = 500  # Prevent unbounded memory growth


def _prune_expired():
    """Remove expired sessions and enforce max session count."""
    now = datetime.now(timezone.utc)
    expired = [
        sid for sid, meta in _session_store.items()
        if (now - meta["created_at"]).total_seconds() > SESSION_EXPIRY_SECONDS
    ]
    for sid in expired:
        del _session_store[sid]

    # Evict oldest sessions if still over capacity
    if len(_session_store) > MAX_SESSIONS:
        sorted_sessions = sorted(
            _session_store.items(),
            key=lambda x: x[1]["created_at"]
        )
        for sid, _ in sorted_sessions[:len(_session_store) - MAX_SESSIONS]:
            del _session_store[sid]


# ─── Text Extraction ──────────────────────────────────────────────────────────

def _extract_text(filename: str, content: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=content, filetype="pdf")
            pages = [page.get_text() for page in doc]
            doc.close()
            text = "\n".join(pages).strip()
            if not text:
                raise ValueError("PDF has no selectable text — may be a scanned image.")
            return text
        except ImportError:
            raise HTTPException(status_code=500, detail="PyMuPDF not installed (pip install PyMuPDF)")

    elif ext == "docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs).strip()
            if not text:
                raise ValueError("DOCX appears to be empty.")
            return text
        except ImportError:
            raise HTTPException(status_code=500, detail="python-docx not installed")

    elif ext in ("txt", "md", "csv"):
        return content.decode("utf-8", errors="ignore").strip()

    # Fallback
    decoded = content.decode("utf-8", errors="ignore").strip()
    if not decoded:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: .{ext}")
    return decoded


# ─── Endpoint 1: Upload + Analyse Document ────────────────────────────────────

@router.post("/analyze-doc")
async def analyze_doc(
    file: UploadFile = File(...),
    student_roll: str = Form(""),
):
    """
    Upload a study document. Returns session_id + AI analysis (summary, topics, key points).
    Use the session_id in /doc/chat to ask follow-up questions.
    """
    _prune_expired()

    raw = await file.read()
    filename = file.filename or "document.txt"

    # Extract text
    try:
        text = _extract_text(filename, raw)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File read error: {str(e)}")

    if not text or len(text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Document is too short or empty.")

    # Truncate for analysis (Capped at 60k to avoid TPM limits)
    analysis_text = text[:60_000]
    if len(text) > 60_000:
        analysis_text += "\n\n[Document truncated for analysis — first 60,000 characters shown]"

    # Store session (full text for chat, capped at 60k)
    session_id = str(uuid.uuid4())
    _session_store[session_id] = {
        "text": text[:60_000],
        "filename": filename,
        "roll": student_roll.upper().strip(),
        "created_at": datetime.now(timezone.utc),
    }
    print(f"[doc] 📄 Session {session_id[:8]}… created | {len(text)} chars | {filename}")

    # Build analysis prompt
    prompt = f"""You are IntelliMind, an expert AI study assistant.

A student has uploaded the following study document:

---DOCUMENT START---
{analysis_text}
---DOCUMENT END---

Analyse this document and provide a comprehensive study guide. Return your response in this exact markdown format:

## 📋 Document Summary
[2-3 sentence overview of what this document covers]

## 🎯 Key Topics Covered
[Bullet list of the main topics/chapters/sections]

## 📌 Important Points
[The most important facts, definitions, or concepts a student must know]

## ❓ Likely Exam Questions
[3-5 questions that are likely to be asked based on this content]

## 💡 Study Tips
[1-2 specific tips for studying this material]

Be thorough and student-focused. Use simple language."""

    data = call_gemini_rest(prompt, max_tokens=2048)
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])

    analysis = extract_text(data)
    if not analysis:
        raise HTTPException(status_code=502, detail="AI returned empty analysis.")

    return {
        "session_id": session_id,
        "filename": filename,
        "char_count": len(text),
        "analysis": analysis,
    }


# ─── Endpoint 2: Chat About the Document ──────────────────────────────────────

class DocChatRequest(BaseModel):
    session_id: str
    question: str
    student_roll: str = ""


@router.post("/doc/chat")
async def doc_chat(request: DocChatRequest):
    """
    Ask a follow-up question about the uploaded document.
    Requires a valid session_id from /analyze-doc.

    FIXED: The document content IS passed to the AI, so it will always
    answer from the document — never say "information not provided".
    """
    _prune_expired()

    session = _session_store.get(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your document."
        )

    doc_text = session["text"]
    filename = session["filename"]
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")

    # ── THE CRITICAL PROMPT FIX ──────────────────────────────────────────────
    # Previously: document was NOT passed to /doc/chat → AI said "info not provided"
    # Now: full document (up to 60k chars) is ALWAYS included in the prompt
    prompt = f"""You are IntelliMind, an expert AI study assistant helping a student prepare for exams.

The student has uploaded a document called "{filename}".
Here is the COMPLETE content of that document:

---DOCUMENT START---
{doc_text}
---DOCUMENT END---

The student's question is: "{question}"

RULES YOU MUST FOLLOW:
1. The document content IS provided above between the markers — do NOT say "information not provided".
2. If the student asks "answer question 1" or "answer the first question", FIND that question in the document and answer it fully.
3. If the student asks about a specific topic, find the relevant section and explain it.
4. Give clear, educational answers — explain concepts, don't just copy text.
5. If a question genuinely isn't covered in the document, say "This topic isn't covered in the uploaded document."
6. Use **bold** for key terms, and structure your answer clearly.

Answer the student's question now:"""

    data = call_gemini_rest(prompt, max_tokens=2048)
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])

    response = extract_text(data)
    if not response:
        raise HTTPException(status_code=502, detail="AI returned an empty response.")

    print(f"[doc/chat] 💬 Session {request.session_id[:8]}… | Q: {question[:60]}…")

    return {
        "response": response,
        "session_id": request.session_id,
        "filename": filename,
    }