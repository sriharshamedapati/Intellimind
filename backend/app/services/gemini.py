"""
gemini.py — Shared Gemini API Client
====================================
Handles all Gemini API communication.
Used by chat, summarizer, and document analysis.

FIXES (Bad Gateway Root Cause):
- gemini-2.5-flash requires v1beta endpoint — NOT v1
- Model cascade now correctly leads with gemini-2.5-flash on v1beta
- Removed deprecated gemini-1.0-pro / gemini-pro (always 404)
- config.py GEMINI_URL is no longer ignored
"""

import time
import requests
from app.config import settings


def call_gemini(
    prompt: str,
    image_data: dict = None,
    *,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    response_mime_type: str = "text/plain",
) -> dict:
    """
    Send prompt (and optional image) to Gemini API and return raw JSON response.
    Uses a model cascade: tries primary model first, falls back on 404/500.
    """

    if not settings.GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not set in .env"}

    parts = [{"text": prompt}]
    if image_data and "data" in image_data and "mime_type" in image_data:
        parts.append(
            {
                "inline_data": {
                    "mime_type": image_data["mime_type"],
                    "data": image_data["data"],
                }
            }
        )

    gen_config: dict = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
    }
    if response_mime_type == "application/json":
        gen_config["response_mime_type"] = "application/json"

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": gen_config,
    }

    _KEY = settings.GEMINI_API_KEY

    # ── Model cascade ──────────────────────────────────────────────────────────
    # CRITICAL: gemini-2.5-flash ONLY works on v1beta, NOT v1.
    # gemini-1.5-flash / gemini-1.5-flash-8b work on v1 (stable).
    # Deprecated models (gemini-1.0-pro, gemini-pro) removed — always 404.
    # ──────────────────────────────────────────────────────────────────────────
    models_to_try = [
        # (model_name, api_version)
        ("gemini-2.5-flash",       "v1beta"),   # PRIMARY — matches config.py
        ("gemini-2.0-flash",       "v1beta"),   # fallback (stable 2.0)
        ("gemini-1.5-flash",       "v1"),       # fallback (free tier stable)
        ("gemini-1.5-flash-8b",    "v1"),       # fallback (lightweight free tier)
    ]

    last_error = ""

    for model, api_ver in models_to_try:
        url = (
            f"https://generativelanguage.googleapis.com/{api_ver}"
            f"/models/{model}:generateContent?key={_KEY}"
        )

        for attempt in range(2):  # 2 tries per model
            try:
                res = requests.post(url, json=payload, timeout=60)

                # ── Success ──
                if res.status_code == 200:
                    json_res = res.json()

                    # Safety block check
                    if not json_res.get("candidates") and json_res.get("promptFeedback"):
                        reason = json_res["promptFeedback"].get("blockReason", "Unknown")
                        print(f"[gemini] ⚠️  Blocked by safety filter: {reason}")
                        return {"error": f"Response blocked by Gemini safety filters: {reason}"}

                    if model != "gemini-2.5-flash":
                        print(f"[gemini] ✅ Succeeded with fallback model: {model} ({api_ver})")
                    else:
                        print(f"[gemini] ✅ {model} ({api_ver}) OK")
                    return json_res

                body_preview = res.text[:300] if res.text else "(empty)"

                # ── Rate limit (429) ── wait and retry same model
                if res.status_code == 429:
                    wait = 8 * (attempt + 1)  # 8s, 16s
                    print(
                        f"[gemini] ⏳ Rate limited on {model} "
                        f"(attempt {attempt + 1}/2), waiting {wait}s…"
                    )
                    time.sleep(wait)
                    continue

                # ── 404 model not found or 5xx server error ── move to next model
                if res.status_code == 404 or res.status_code >= 500:
                    label = "NOT_FOUND" if res.status_code == 404 else f"HTTP {res.status_code}"
                    print(
                        f"[gemini] ⚠️  {model} ({api_ver}) → {label} "
                        f"(attempt {attempt + 1}/2)"
                    )
                    last_error = f"{model} → {label}"
                    time.sleep(2 * (attempt + 1))
                    continue

                # ── Other 4xx (bad key, bad request) ── no point retrying
                print(f"[gemini] ❌ {model} returned {res.status_code}: {body_preview}")
                return {
                    "error": f"Gemini API error {res.status_code}: {body_preview[:200]}"
                }

            except requests.exceptions.Timeout:
                print(f"[gemini] ⏳ Timeout on {model} (attempt {attempt + 1}/2)")
                last_error = f"{model} → Timeout"
                time.sleep(2)
            except requests.exceptions.ConnectionError as e:
                print(f"[gemini] 🔌 Connection error on {model}: {e}")
                last_error = f"{model} → ConnectionError"
                time.sleep(2)
            except Exception as e:
                print(f"[gemini] ❌ {model} failed: {type(e).__name__}: {e}")
                last_error = f"{model} → {type(e).__name__}"
                time.sleep(2)

        print(f"[gemini] ➡️  Moving to next model (failed: {model})")

    return {
        "error": (
            f"All Gemini models unavailable. Last error: {last_error}. "
            "Please try again in a minute."
        )
    }


# Alias used by doc.py and resume.py
call_gemini_rest = call_gemini


def extract_text(res: dict) -> str:
    """Extract the generated text from a Gemini API response."""
    try:
        candidates = res.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)
            if text.strip():
                return text.strip()

        if "text" in res:
            return res["text"]

        if "output_text" in res:
            return res["output_text"]

        # Candidate exists but text is empty — check finish reason
        if candidates and not text.strip():
            finish_reason = candidates[0].get("finishReason")
            if finish_reason:
                print(f"[gemini] ⚠️  Candidate failed with reason: {finish_reason}")
                return f"[Blocked by safety: {finish_reason}]"

    except Exception as e:
        print(f"[gemini] extract_text error: {type(e).__name__}: {e}")

    return ""