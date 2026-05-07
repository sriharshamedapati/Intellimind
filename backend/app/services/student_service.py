"""
student_service.py — Student Data Access Layer
================================================
All Supabase RPC calls and student-related DB queries.

FIXES:
- Added None safety checks for supabase client
- Removed debug print statement
"""
from app.db import supabase


def _check_db():
    """Return True if Supabase is available, False otherwise."""
    if supabase is None:
        print("[student_service] ⚠️  Supabase not available — skipping DB operation")
        return False
    return True


def get_student_summary(student_roll: str):
    if not _check_db():
        return None
    try:
        r = supabase.rpc("get_student_summary", {"student_roll": student_roll}).execute()
        return r.data
    except Exception as e:
        print(f"[student_service] get_student_summary error: {e}")
        return None


def get_student_activity(student_roll: str):
    if not _check_db():
        return None
    try:
        r = supabase.rpc("get_student_activity", {"student_roll": student_roll}).execute()
        return r.data
    except Exception as e:
        print(f"[student_service] get_student_activity error: {e}")
        return None


def get_recent_activity(student_roll: str):
    if not _check_db():
        return None
    try:
        r = supabase.rpc("get_recent_activity", {"student_roll": student_roll}).execute()
        return r.data
    except Exception as e:
        print(f"[student_service] get_recent_activity error: {e}")
        return None


def get_recent_summaries(user_id: str) -> list[str]:
    """Fetch the 5 most recent chat summaries for memory context."""
    if not _check_db():
        return []
    try:
        result = (
            supabase.table("chat_summary")
            .select("summary")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        return [r["summary"] for r in result.data]
    except Exception as e:
        print(f"[student_service] get_recent_summaries error: {e}")
        return []


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