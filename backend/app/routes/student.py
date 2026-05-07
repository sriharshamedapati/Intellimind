"""
student.py — Student Data REST Endpoints
==========================================
GET /student-summary/{roll}
GET /student-activity/{roll}
GET /recent-activity/{roll}
"""
from fastapi import APIRouter, HTTPException
from app.services.student_service import (
    get_student_summary,
    get_student_activity,
    get_recent_activity,
)

router = APIRouter()


@router.get("/student-summary/{roll}")
def student_summary(roll: str):
    data = get_student_summary(roll.upper().strip())
    if data is None:
        raise HTTPException(status_code=404, detail=f"No summary found for roll {roll}")
    return {"roll": roll.upper(), "summary": data}


@router.get("/student-activity/{roll}")
def student_activity(roll: str):
    data = get_student_activity(roll.upper().strip())
    if data is None:
        raise HTTPException(status_code=404, detail=f"No activity found for roll {roll}")
    return {"roll": roll.upper(), "activity": data}


@router.get("/recent-activity/{roll}")
def recent_activity(roll: str):
    data = get_recent_activity(roll.upper().strip())
    if data is None:
        raise HTTPException(status_code=404, detail=f"No recent activity for roll {roll}")
    return {"roll": roll.upper(), "recent_activity": data}
