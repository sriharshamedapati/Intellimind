"""
maya_service.py — Maya Platform Data Fetcher
==============================================
Fetches student problem counts, dashboard data, and skill tags
from the Maya Technical Hub external API.
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAYA_BASE_URL = "https://maya.technicalhub.io/node/api"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}


def _post(endpoint: str, roll_no: str) -> dict:
    """Internal helper — POST to Maya API with error handling."""
    try:
        res = requests.post(
            f"{MAYA_BASE_URL}/{endpoint}",
            json={"roll_no": roll_no},
            headers=HEADERS,
            timeout=10,
            verify=False,
        )
        return res.json()
    except Exception as e:
        return {"error": str(e)}


def get_problem_count(roll_no: str) -> dict:
    return _post("get-student-problems-count", roll_no)


def get_problem_dashboard(roll_no: str) -> dict:
    return _post("get-student-problems-count-dashboard", roll_no)


def get_skill_tags_details(roll_no: str) -> dict:
    return _post("get-tags-counts", roll_no)
