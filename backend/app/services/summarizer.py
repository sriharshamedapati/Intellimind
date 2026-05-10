"""
summarizer.py — Chat Summarization Service
============================================
Calls Gemini to extract topics, strengths, weaknesses from a chat message.
"""
import json
import re
from app.services.gemini import call_gemini, extract_text


def summarize_chat(chat_message: str, memory_context: str = "") -> dict:
    """Analyze a chat message and return structured summary data."""

    prompt = f"""You are an AI learning analyzer.

You MUST analyze BOTH:
1. Current message
2. Past learning history

Return ONLY valid JSON.

Format:
{{
"topics": [],
"strengths": [],
"weaknesses": [],
"behavior": "",
"summary": ""
}}

IMPORTANT:
- If the question is about performance (like "what am I weak at"),
  you MUST use past history to infer weaknesses.
- Identify repeated weak areas across history.
- DO NOT return empty fields.

━━━━━━━━━━━━━━━━━━
PAST HISTORY:
{memory_context}

━━━━━━━━━━━━━━━━━━
CURRENT MESSAGE:
{chat_message}
"""

    try:
        data = call_gemini(prompt)

        if "error" in data:
            return {"error": data["error"]}

        text = extract_text(data)
        if not text:
            return {"error": "Invalid Gemini response"}

        print(f"[summarizer] 🔍 Raw output: {text[:200]}...")

        # Strip markdown code fences if Gemini wrapped JSON in ```json ... ```
        text = text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()

        # Extract JSON using regex
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return {"error": "Invalid JSON format", "raw": text}

        return {"error": "No JSON found", "raw": text}

    except Exception as e:
        print(f"[summarizer] ❌ Error: {e}")
        return {"error": str(e)}


def calculate_score(summary_data: dict) -> int:
    """
    Score a chat session based on summarized topics, strengths, and weaknesses.
    Returns 0–100.
    """
    if not summary_data or "error" in summary_data:
        return 0

    topics = summary_data.get("topics", [])
    strengths = summary_data.get("strengths", [])
    weaknesses = summary_data.get("weaknesses", [])

    # Base score from topic coverage
    topic_score = min(len(topics) * 15, 40)

    # Strength bonus
    strength_score = min(len(strengths) * 12, 35)

    # Weakness penalty (fewer = better)
    weakness_penalty = min(len(weaknesses) * 8, 25)

    score = topic_score + strength_score + (25 - weakness_penalty)
    return max(0, min(score, 100))