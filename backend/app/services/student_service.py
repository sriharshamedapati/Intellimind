"""
student_service.py — Student Data Access Layer
================================================
Handles all Supabase queries for student data including
chat summaries, user ID resolution, and session persistence.
"""
from app.config import settings
from app.db import supabase


def _check_db():
    """Return True if Supabase is available, False otherwise."""
    if supabase is None:
        print("[student_service] ⚠️  Supabase not available — skipping DB operation")
        return False
    return True


def get_student_memory(user_id: str, limit: int = None) -> list[dict]:
    """Fetch recent chat summaries with full context (topics, weaknesses, scores)."""
    if not _check_db():
        return []
    
    fetch_limit = limit or settings.MEMORY_LIMIT
    try:
        result = (
            supabase.table("chat_summary")
            .select("summary, topics, strengths, weaknesses, score, date")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(fetch_limit)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"[student_service] get_student_memory error: {e}")
        return []


def get_recent_summaries(user_id: str) -> list[str]:
    """Backward compatible wrapper — returns only summary strings."""
    memory = get_student_memory(user_id)
    return [r["summary"] for r in memory if r.get("summary")]


def save_chat_summary(roll: str, summary_data: dict, score: int):
    """Persist a chat summary to Supabase."""
    if not _check_db():
        return
    try:
        supabase.table("chat_summary").insert({
            "user_id": roll,
            "topics": summary_data.get("topics", []),
            "strengths": summary_data.get("strengths", []),
            "weaknesses": summary_data.get("weaknesses", []),
            "summary": summary_data.get("summary", ""),
            "score": score,
        }).execute()
        print("[student_service] ✅ Summary saved to Supabase")
    except Exception as e:
        print(f"[student_service] ❌ DB insert error: {e}")


def get_user_id(roll_no: str) -> str:
    if not _check_db():
        return None
    try:
        r = supabase.rpc("get_user_id", {"p_roll_no": roll_no}).execute()

        # Case 1: direct string
        if isinstance(r.data, str):
            return r.data

        # Case 2: list of dicts
        if isinstance(r.data, list) and len(r.data) > 0:
            return r.data[0].get("user_id")

        return None

    except Exception as e:
        print(f"[student_service] get_user_id error: {e}")
        return None