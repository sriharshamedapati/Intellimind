"""
gemini.py — Shared Gemini API Client
====================================
Handles all Gemini API communication with aggressive retry logic.
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
    if not settings.GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not set in .env"}

    parts = [{"text": prompt}]
    if image_data and "data" in image_data and "mime_type" in image_data:
        parts.append({
            "inline_data": {
                "mime_type": image_data["mime_type"],
                "data": image_data["data"],
            }
        })

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
    # VERIFIED via /v1beta/models — only these models exist on this API key.
    # All 1.5 models are GONE (404). Use 2.x+ only.
    # Lite models have SEPARATE rate-limit buckets → great fallback for 429.
    # ──────────────────────────────────────────────────────────────────────────
    models_to_try = [
        # (model_name, api_version, max_retries)
        ("gemini-2.0-flash",           "v1beta", 3),   # PRIMARY (latest stable)
        ("gemini-2.0-flash-lite",      "v1beta", 2),   # Lite = separate quota
        ("gemini-flash-lite-latest",   "v1beta", 2),   # Final lite fallback
    ]

    last_error = ""

    for model, api_ver, max_retries in models_to_try:
        url = (
            f"https://generativelanguage.googleapis.com/{api_ver}"
            f"/models/{model}:generateContent?key={_KEY}"
        )

        for attempt in range(max_retries):
            try:
                res = requests.post(url, json=payload, timeout=90)

                # ── Success ──
                if res.status_code == 200:
                    json_res = res.json()

                    # Safety block check
                    if not json_res.get("candidates") and json_res.get("promptFeedback"):
                        reason = json_res["promptFeedback"].get("blockReason", "Unknown")
                        print(f"[gemini] [WARN] Blocked by safety filter: {reason}")
                        return {"error": f"Response blocked by Gemini safety filters: {reason}"}

                    print(f"[gemini] [OK] {model} ({api_ver}) OK")
                    return json_res

                body_preview = res.text[:300] if res.text else "(empty)"

                # ── Rate limit (429) ── wait and retry same model
                if res.status_code == 429:
                    wait = 10 * (attempt + 1)  # 10s, 20s, 30s, 40s, 50s
                    print(
                        f"[gemini] ⏳ Rate limited on {model} "
                        f"(attempt {attempt + 1}/{max_retries}), waiting {wait}s…"
                    )
                    time.sleep(wait)
                    continue

                # ── 503 server overload ── retry same model (transient)
                if res.status_code >= 500:
                    print(
                        f"[gemini] [WARN] {model} -> HTTP {res.status_code} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    last_error = f"{model} -> HTTP {res.status_code}"
                    time.sleep(5 * (attempt + 1))
                    continue

                # ── 404 model not found ── skip to next model immediately
                if res.status_code == 404:
                    print(f"[gemini] [WARN] {model} ({api_ver}) -> NOT_FOUND — skipping")
                    last_error = f"{model} -> NOT_FOUND"
                    break

                # ── Other 4xx (bad key, bad request) ── no point retrying
                print(f"[gemini] [ERROR] {model} returned {res.status_code}: {body_preview}")
                return {
                    "error": f"Gemini API error {res.status_code}: {body_preview[:200]}"
                }

            except requests.exceptions.Timeout:
                print(f"[gemini] ⏳ Timeout on {model} (attempt {attempt + 1}/{max_retries})")
                last_error = f"{model} → Timeout"
                time.sleep(3)
            except requests.exceptions.ConnectionError as e:
                print(f"[gemini] 🔌 Connection error on {model}: {e}")
                last_error = f"{model} → ConnectionError"
                time.sleep(3)
            except Exception as e:
                print(f"[gemini] [ERROR] {model} failed: {type(e).__name__}: {e}")
                last_error = f"{model} -> {type(e).__name__}"
                time.sleep(2)

        print(f"[gemini] [INFO] Moving to next model (failed: {model})")

    return {"error": f"All Gemini models failed. Last error: {last_error}"}


call_gemini_rest = call_gemini


def extract_text(res: dict) -> str:
    try:
        candidates = res.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)
            if text.strip():
                return text.strip()
    except Exception:
        pass
    return ""