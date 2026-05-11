"""
chat.py — Chat Route (Smart Token Management)
===============================================
POST /chat  →  AI-powered tutoring with intent-based data fetching.
Only fetches the data sources that the student's question actually needs.
"""
import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import get_current_user, verify_student_roll

from app.services.gemini import call_gemini, extract_text
from app.services.intent import detect_intent
from app.services.hoot_data import get_hoot_data
from app.services.prompts import get_prompt
from app.services.maya_service import (
    get_problem_count,
    get_problem_dashboard,
    get_skill_tags_details,
)
from app.services.student_service import get_student_memory, save_chat_summary, get_user_id
from app.services.summarizer import summarize_chat, calculate_score
from app.services.recommender import generate_recommendations

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    student_roll: str
    mode: str = "chat"  # chat | voice
    image_base64: str | None = None
    image_mime_type: str | None = None


@router.post("/chat")
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    roll = request.student_roll.upper().strip()

    if not roll:
        raise HTTPException(status_code=400, detail="student_roll is required")

    if not re.match(r"^[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{4}$", roll):
        raise HTTPException(status_code=422, detail="Invalid roll number format. Expected format: 22A91A0501")

    # Security: Verify that the authenticated user is accessing their own data
    verify_student_roll(roll, user)
    message = request.message.strip()
    mode = request.mode.lower()

    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    # ── 1. Detect intent ──
    intents = detect_intent(message)
    print(f"[chat] [INTENT] Intents detected: {intents} | Message: {message[:80]}")

    # ── 2. Smart data fetching — only fetch what's needed ──
    data = {
        "roll": roll,
        "message": message,
    }

    # Memory: needed for memory, performance, or placement intents
    if "memory" in intents or "performance" in intents or "placement" in intents:
        past_sessions = get_student_memory(roll)
        if past_sessions:
            formatted_history = []
            for i, s in enumerate(past_sessions):
                date_str = s.get("date", "Unknown Date")[:10]
                session_block = (
                    f"--- SESSION {i+1} ({date_str}) ---\n"
                    f"Summary: {s.get('summary')}\n"
                    f"Topics: {', '.join(s.get('topics', []))}\n"
                    f"Weaknesses: {', '.join(s.get('weaknesses', []))}\n"
                    f"Score: {s.get('score')}/100"
                )
                formatted_history.append(session_block)
            
            memory_context = "\n\n".join(formatted_history)
            data["memory"] = memory_context
            print(f"[chat] 📚 Fetched memory ({len(past_sessions)} sessions)")
        else:
            data["memory"] = None
            print(f"[chat] 📚 No previous sessions found for memory")
    else:
        data["memory"] = None

    # Maya data: needed for maya, performance, or placement intents
    if "maya" in intents or "performance" in intents or "placement" in intents:
        data["problem_cnt"] = get_problem_count(roll)
        data["problem_dashboard"] = get_problem_dashboard(roll)
        data["skill_tags"] = get_skill_tags_details(roll)
        print(f"[chat] 🧑‍💻 Fetched Maya data (problems + skill tags)")
    else:
        data["problem_cnt"] = None
        data["problem_dashboard"] = None
        data["skill_tags"] = None

    # Hoot data: needed for hoot, performance, or placement intents
    if "hoot" in intents or "performance" in intents or "placement" in intents:
        user_id = get_user_id(roll)
        if user_id:
            data["hoot_data"] = get_hoot_data(user_id)
            print(f"[chat] [HOOT] Fetched Hoot LSRW data")
        else:
            data["hoot_data"] = None
            print(f"[chat] [WARN] Could not resolve user_id for Hoot data")
    else:
        data["hoot_data"] = None

    # Log what was skipped
    skipped = []
    if data["memory"] is None and "memory" not in intents:
        skipped.append("memory")
    if data["problem_cnt"] is None and "maya" not in intents:
        skipped.append("maya")
    if data["hoot_data"] is None and "hoot" not in intents:
        skipped.append("hoot")
    if skipped:
        print(f"[chat] ⏭️ Skipped: {', '.join(skipped)} (not needed for this query)")

    # ── 3. Build prompt and call Gemini ──
    prompt = get_prompt(mode, data)
    
    image_data = None
    if request.image_base64 and request.image_mime_type:
        image_data = {
            "mime_type": request.image_mime_type,
            "data": request.image_base64
        }
        
    # Use higher token limit for chat (detailed analysis), lower for voice (concise)
    max_tokens = 1024 if mode == "voice" else 8192
    res = call_gemini(prompt, image_data=image_data, max_tokens=max_tokens)

    if "error" in res:
        raise HTTPException(status_code=502, detail=res["error"])

    response_text = extract_text(res)
    if not response_text:
        print(f"[chat] Unexpected Gemini response: {res}")
        raise HTTPException(status_code=502, detail="Unexpected response from AI.")

    print(f"[chat] 📩 {mode.upper()} | {roll}: {message[:80]}...")

    # ── 4. Post-processing (Quota Protection) ──
    # To prevent 429 Rate Limits, we skip summarization if:
    # 1. We are in voice mode (requires low latency)
    # 2. It was a simple greeting/short message (detect via length)
    if mode == "chat" and len(message) > 10:
        print(f"[chat] 📝 Running background summarizer...")
        memory_ctx = data.get("memory") or ""
        summary_data = summarize_chat(message, memory_ctx)
        
        # Only do recommendations if summary succeeded
        if "error" not in summary_data:
            recommendations = generate_recommendations(summary_data)
            score = calculate_score(summary_data)
            save_chat_summary(roll, summary_data, score)
        else:
            print(f"[chat] ⚠️ Summarizer skipped due to AI error: {summary_data.get('error')}")
            summary_data = {"summary": "Summary unavailable due to high demand."}
            recommendations = []
    else:
        # Minimal response for voice/short messages to save quota
        summary_data = {}
        recommendations = []

    return {
        "response": response_text,
        "summary": summary_data,
        "recommendations": recommendations,
        "student_roll": roll,
        "mode": mode,
        "intents_detected": intents,
    }