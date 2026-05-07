"""
hoot_data.py — Hoot Platform Data Fetcher
==========================================
Fetches student LSRW module attempt data from the Hoot (aihoot.in) API.
"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOOT_URL = "https://aihoot.in:5001/api/get-individual-module-attempts-by-user-id"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}


def _post(user_id: str) -> dict:
    try:
        res = requests.post(
            HOOT_URL,
            json={"user_id": user_id},
            headers=HEADERS,
            timeout=10,
            verify=False,
        )
        res.raise_for_status()
        return res.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def transform_data(data: dict) -> dict:
    result = {}

    # sections like listening, speaking, etc.
    for section, content in data.items():
        if isinstance(content, dict) and "records" in content:
            result[section] = {
                "records": [
                    {
                        "count": r.get("count"),
                        "module_name": r.get("module_name"),
                        "complexity": r.get("complexity"),
                        "percentage": r.get("percentage"),
                    }
                    for r in content.get("records", [])
                ],
                "noofattempts": content.get("no_attempts"),
                "percentage": content.get("percentage"),
            }

    # top-level fields
    result["total_attempts"] = data.get("total_attempts")
    result["userpercentage"] = data.get("user_percentage")

    return result


def get_hoot_data(user_id: str) -> dict:
    response = _post(user_id)

    if "error" in response:
        return response

    return transform_data(response)
