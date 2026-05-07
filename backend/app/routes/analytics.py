"""
analytics.py — Progress Analytics Route
=========================================
GET /progress/{user_id}

FIXES:
- Added null safety for supabase client
"""
from fastapi import APIRouter, HTTPException
from app.db import supabase

router = APIRouter()


@router.get("/progress/{user_id}")
def get_progress(user_id: str):
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        data = (
            supabase.table("chat_summary")
            .select("date, score")
            .eq("user_id", user_id)
            .execute()
        )
        return data.data
    except Exception as e:
        print(f"[analytics] ❌ Error fetching progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress data: {str(e)}")