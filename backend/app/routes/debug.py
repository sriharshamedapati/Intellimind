"""
debug.py — Diagnostic Endpoints (Development Only)
====================================================
GET /debug/student/{roll}
GET /debug/tables
GET /debug/gemini         ← Test Gemini API key

Automatically disabled when ENVIRONMENT=production.
"""
import os
import requests
from fastapi import APIRouter, HTTPException
from app.db import supabase
from app.config import settings
from app.services.gemini import call_gemini, extract_text

router = APIRouter()

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"


def _guard():
    """Block debug endpoints in production."""
    if IS_PRODUCTION:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/debug/student/{roll}")
def debug_student(roll: str):
    """Raw output from every Supabase RPC + connection info."""
    _guard()
    roll = roll.upper().strip()

    if not supabase:
        return {"error": "Supabase client not initialized. Check .env credentials."}

    results = {
        "roll_tested": roll,
        "supabase_url": os.getenv("SUPABASE_URL", "NOT SET"),
        "rpcs": {},
    }

    for rpc_name in ["get_student_summary", "get_student_activity", "get_recent_activity"]:
        try:
            r = supabase.rpc(rpc_name, {"student_roll": roll}).execute()
            results["rpcs"][rpc_name] = {
                "status": "success",
                "data": r.data,
                "count": len(r.data) if isinstance(r.data, list) else "not a list",
                "is_empty": not r.data,
            }
        except Exception as e:
            results["rpcs"][rpc_name] = {"status": "error", "error": str(e)}

    # Direct table test
    try:
        r = supabase.table("login_logs").select("*").limit(3).execute()
        results["direct_table_test"] = {
            "table": "login_logs",
            "status": "success",
            "rows_found": len(r.data) if r.data else 0,
            "sample": r.data[:2] if r.data else [],
        }
    except Exception as e:
        results["direct_table_test"] = {
            "table": "login_logs",
            "status": "error",
            "error": str(e),
            "hint": "If this errors, the SUPABASE_URL/KEY in .env might be wrong",
        }

    return results


@router.get("/debug/tables")
def debug_tables():
    _guard()
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "NOT SET"),
        "key_prefix": os.getenv("SUPABASE_KEY", "")[:20] + "...",
        "supabase_connected": supabase is not None,
        "message": "Check /debug/student/{roll} for RPC diagnostics",
    }


@router.get("/debug/gemini")
def debug_gemini():
    """
    Test Gemini API key validity by making a minimal request.
    Returns: key status, model info, and a test response.
    """
    _guard()
    result = {
        "api_key_set": bool(settings.GEMINI_API_KEY),
        "api_key_suffix": f"...{settings.GEMINI_API_KEY[-6:]}" if settings.GEMINI_API_KEY else "NOT SET",
        "model": settings.GEMINI_MODEL,
        "gemini_url": settings.GEMINI_URL.split("?")[0] + "?key=***",
    }

    if not settings.GEMINI_API_KEY:
        result["status"] = "FAIL"
        result["error"] = "GEMINI_API_KEY is not set in .env"
        return result

    # Test 1: List available models
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GEMINI_API_KEY}"
        res = requests.get(list_url, timeout=10)
        if res.status_code == 200:
            models_data = res.json()
            model_names = [m.get("name", "") for m in models_data.get("models", [])]
            target = f"models/{settings.GEMINI_MODEL}"
            result["models_accessible"] = len(model_names)
            result["target_model_available"] = target in model_names
            if not result["target_model_available"]:
                # Check for partial match
                matching = [m for m in model_names if settings.GEMINI_MODEL in m]
                result["similar_models"] = matching[:5]
        else:
            result["models_list_error"] = f"HTTP {res.status_code}: {res.text[:200]}"
    except Exception as e:
        result["models_list_error"] = str(e)

    # Test 2: Simple generation test using central service
    try:
        data = call_gemini("Reply with exactly: INTELLIMIND_OK", temperature=0, max_tokens=20)
        
        if "error" in data:
            result["status"] = "FAIL"
            result["error"] = data["error"]
            # Detect specific common errors for better debugging info
            err = str(data["error"])
            if "429" in err: result["status"] = "RATE_LIMITED"
            if "403" in err: result["status"] = "FORBIDDEN"
            if "400" in err: result["status"] = "BAD_REQUEST"
        else:
            text = extract_text(data)
            result["status"] = "OK"
            result["test_response"] = text.strip()

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result
