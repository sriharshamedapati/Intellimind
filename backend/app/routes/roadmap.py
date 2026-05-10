"""
roadmap.py — Roadmap Planner Route
=====================================
AI-generated personalised study plans based on student performance data.

Endpoints:
    POST   /roadmap/generate                → Generate AI study plan (max 3/month)
    GET    /roadmap/plans/{roll}             → List all plans for a student
    PATCH  /roadmap/plans/{plan_id}/activate → Set plan as active
    PATCH  /roadmap/tasks/{task_id}/complete → Mark task done
    GET    /roadmap/active/{roll}            → Get active plan + today's task

Rules:
    - Only 1 active plan at a time
    - Students must complete the current plan before generating a new one
    - Max 3 plans per month
    - Duration options: 7, 15, 21, or 30 days
"""

import re
import json
import random
from datetime import datetime, timezone
from collections import Counter, defaultdict

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import get_current_user, verify_student_roll

from app.db import supabase
from app.services.maya_service import get_skill_tags_details

from app.config import settings
from app.services.gemini import call_gemini, extract_text

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

VALID_DURATIONS = (7, 15, 21, 30)
MAX_PLANS_PER_MONTH = 3

def _check_db():
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database unavailable")




# ─── Student Profile ─────────────────────────────────────────────────────────

def _get_student_profile(roll: str) -> dict:
    """Pull weak topics + avg score from Supabase chat_summary + Maya skill tags."""
    profile = {"weak_topics": "General CS fundamentals", "weak_tags": [], "avg_score": 50.0}

    # From chat_summary
    try:
        result = (
            supabase.table("chat_summary")
            .select("weaknesses, topics, score")
            .eq("user_id", roll)
            .order("date", desc=True)
            .limit(10)
            .execute()
        )
        if result.data:
            all_weaknesses, scores = [], []
            for r in result.data:
                if r.get("weaknesses"):
                    all_weaknesses.extend(r["weaknesses"])
                if r.get("score") is not None:
                    scores.append(float(r["score"]))
            freq = Counter(all_weaknesses)
            ranked = [w for w, _ in freq.most_common(8)]
            if ranked:
                profile["weak_topics"] = "; ".join(ranked)
            if scores:
                profile["avg_score"] = round(sum(scores) / len(scores), 1)
    except Exception as e:
        print(f"[roadmap] ❌ chat_summary fetch error: {e}")

    # From Maya skill tags (low count = weak area)
    try:
        tags_data = get_skill_tags_details(roll)
        items = []
        if isinstance(tags_data, list):
            items = tags_data
        elif isinstance(tags_data, dict) and "data" in tags_data:
            items = tags_data["data"]
        low_tags = [
            (item.get("tag") or item.get("name") or "").strip()
            for item in items
            if isinstance(item, dict) and (item.get("count", 99) or 99) < 5
        ]
        profile["weak_tags"] = [t for t in low_tags if t]
    except Exception as e:
        print(f"[roadmap] ❌ Maya tags fetch error: {e}")

    return profile


# ─── Offline Fallback Plan ────────────────────────────────────────────────────

TOPIC_POOLS = {
    "data structures": [
        "Practice Arrays and Strings: solve 5 LeetCode easy problems on two-pointer and sliding window techniques (2-3 hrs).",
        "Study Linked Lists: implement singly and doubly linked lists from scratch, then solve 3 reversal problems (2 hrs).",
        "Master Stacks and Queues: implement using arrays/lists, solve bracket matching and next greater element problems (2 hrs).",
        "Learn Trees: study BST insertion/deletion, implement inorder/preorder/postorder traversal (2-3 hrs).",
        "Study Graphs: implement BFS and DFS, solve connected components and path-finding problems (3 hrs).",
        "Practice Hashing: solve 5 problems using hash maps — frequency count, two sum, group anagrams (2 hrs).",
        "Study Heaps and Priority Queues: implement min-heap, solve top-K elements problems (2 hrs).",
    ],
    "algorithms": [
        "Study Sorting Algorithms: implement bubble, merge, and quick sort; analyse time complexity (2 hrs).",
        "Practice Binary Search: solve 5 variations — rotated array, search range, peak element (2 hrs).",
        "Learn Dynamic Programming basics: solve Fibonacci, coin change, and 0/1 knapsack (3 hrs).",
        "Study Recursion and Backtracking: solve N-Queens, subsets, and permutations problems (2-3 hrs).",
        "Practice Greedy Algorithms: solve activity selection, fractional knapsack, interval scheduling (2 hrs).",
    ],
    "dbms": [
        "Revise SQL basics: practice SELECT, JOIN, GROUP BY, HAVING on sample datasets (2 hrs).",
        "Study Database Normalization: 1NF, 2NF, 3NF with examples and conversion (2 hrs).",
        "Learn Transactions and ACID: study atomicity, consistency, isolation, durability (2 hrs).",
        "Practice ER Diagrams: design schemas for e-commerce, library, and hospital systems (2 hrs).",
        "Study Indexing and Query Optimisation: learn B-tree indexes and explain plans (2 hrs).",
    ],
    "os": [
        "Study Process Management: process states, PCB, context switching, scheduling (2 hrs).",
        "Learn CPU Scheduling: implement FCFS, SJF, Round Robin; calculate waiting times (2 hrs).",
        "Study Memory Management: paging, segmentation, page replacement algorithms (2 hrs).",
        "Revise Deadlock: Coffman conditions, prevention, avoidance (Banker's algorithm) (2 hrs).",
        "Study File Systems: directory structures, inode, FAT, ext4 basics (2 hrs).",
    ],
    "networks": [
        "Study OSI and TCP/IP Models: each layer's function, protocols, and data units (2 hrs).",
        "Learn IP Addressing: subnetting, CIDR notation, calculate network/broadcast addresses (2 hrs).",
        "Study Routing Protocols: RIP, OSPF, BGP — distance vector vs link state (2 hrs).",
        "Revise Transport Layer: TCP vs UDP, 3-way handshake, flow and congestion control (2 hrs).",
        "Study Application Layer: DNS, HTTP/HTTPS, SMTP, FTP (2 hrs).",
    ],
    "aptitude": [
        "Practice Quantitative Aptitude: 20 problems on percentages, profit-loss, ratios (1.5 hrs).",
        "Work on Number Systems: binary, octal, hex conversions and arithmetic (1.5 hrs).",
        "Solve Time-Speed-Distance and Work problems: 15 questions with shortcut methods (1.5 hrs).",
        "Practice Logical Reasoning: series completion, coding-decoding, blood relations (1.5 hrs).",
        "Work on Verbal Ability: reading comprehension, sentence correction, vocabulary (1.5 hrs).",
    ],
    "general": [
        "Revise OOP: encapsulation, inheritance, polymorphism with Java/Python examples (2 hrs).",
        "Practice Coding: solve 5 medium-difficulty problems on LeetCode or HackerRank (2 hrs).",
        "Study System Design basics: scalability, load balancing, caching, sharding (2 hrs).",
        "Work on Soft Skills: practice mock interview answers, prepare STAR stories (1.5 hrs).",
        "Revise Computer Networks + OS integration topics common in placement exams (2 hrs).",
        "Take a full-length aptitude mock test (60 min) and analyse mistakes (2 hrs).",
        "Solve a mix of DS+Algo: 3 easy + 2 medium problems timed at 2 min each (2 hrs).",
    ],
}

KEYWORD_MAP = [
    (["data structure", "array", "linked", "tree", "graph", "heap", "stack", "queue"], "data structures"),
    (["algorithm", "sort", "search", "dynamic", "recursion", "greedy", "backtrack"], "algorithms"),
    (["sql", "database", "dbms", "normali", "er diagram", "transaction", "acid"], "dbms"),
    (["os", "operating", "process", "memory", "deadlock", "scheduling", "paging"], "os"),
    (["network", "tcp", "ip", "protocol", "osi", "routing", "subnet", "http", "dns"], "networks"),
    (["aptitude", "quantitative", "reasoning", "verbal", "percentage", "ratio"], "aptitude"),
]


def _generate_fallback_plan(weak_topics: str, duration_days: int, avg_score: float, weak_tags: list, topic: str = "") -> dict:
    """Generate a personalised study plan without Gemini."""

    # Merge Maya tags and user requested topic into weak topics
    if weak_tags:
        weak_topics = weak_topics + "; " + "; ".join(weak_tags)
    if topic:
        weak_topics = topic + "; " + weak_topics

    weak_lower = weak_topics.lower()
    pool_weights = defaultdict(int)
    for keywords, pool_key in KEYWORD_MAP:
        if any(kw in weak_lower for kw in keywords):
            weight = 3 if avg_score < 40 else (2 if avg_score < 65 else 1)
            pool_weights[pool_key] += weight
    pool_weights["general"] = max(1, pool_weights.get("general", 1))

    weighted_pool = []
    for pool_key, weight in pool_weights.items():
        if pool_key in TOPIC_POOLS:
            tasks = list(TOPIC_POOLS[pool_key])
            random.shuffle(tasks)
            quota = min(weight * 3, len(tasks))
            weighted_pool.extend(tasks[:quota])

    if not weighted_pool:
        weighted_pool = list(TOPIC_POOLS["general"])

    seen, unique_pool = set(), []
    for t in weighted_pool:
        if t not in seen:
            seen.add(t)
            unique_pool.append(t)
    random.shuffle(unique_pool)

    tasks = [
        {"day": day, "description": unique_pool[(day - 1) % len(unique_pool)]}
        for day in range(1, duration_days + 1)
    ]

    top_area = list(pool_weights.keys())[0].title() if pool_weights else "General"
    return {"title": f"{duration_days}-Day Personalised Plan · Focus: {top_area}", "tasks": tasks}


# ─── Gemini Plan Generator ────────────────────────────────────────────────────

def _generate_plan_with_gemini(roll: str, duration_days: int, topic: str = "") -> dict:
    profile = _get_student_profile(roll)
    weak_topics = profile["weak_topics"]
    
    target_focus = f"Student requested topic: {topic}" if topic else f"Student's weak topics: {weak_topics}"

    prompt = (
        f"You are a JSON API. Output ONLY valid JSON. No explanation, no markdown.\n\n"
        f"Create a {duration_days}-day study plan for an engineering student.\n"
        f"{target_focus}\n"
        f"(If they requested a specific topic, focus the plan primarily on that. Otherwise, focus on their weak topics.)\n\n"
        f"Requirements:\n"
        f"- Exactly {duration_days} task objects in the tasks array\n"
        f"- Each task has: \"day\" (integer 1-{duration_days}) and \"description\" (1-2 sentences, specific and actionable, 2-3 hrs each)\n"
        f"- Mix core topic study + coding practice + aptitude where appropriate\n\n"
        f'Output: {{"title": "<short plan name>", "tasks": [{{"day": 1, "description": "..."}}]}}'
    )

    data = call_gemini(prompt, response_mime_type="application/json")
    if "error" in data:
        print(f"[roadmap] ⚠️ Gemini unavailable — using fallback: {data['error']}")
        return _generate_fallback_plan(
            weak_topics, duration_days,
            profile["avg_score"], profile["weak_tags"], topic
        )

    def _parse(text: str) -> dict:
        text = text.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if m:
            text = m.group(1).strip()
        m2 = re.search(r"\{[\s\S]*\}", text)
        if m2:
            text = m2.group(0)
        text = re.sub(r",\s*([\]\}])", r"\1", text)  # trailing commas
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        parsed = json.loads(text)
        if "title" not in parsed or "tasks" not in parsed:
            raise ValueError(f"Missing keys: {list(parsed.keys())}")
        normalised = []
        for idx, t in enumerate(parsed["tasks"]):
            day = t.get("day") or t.get("day_number") or (idx + 1)
            desc = t.get("description") or t.get("task") or t.get("text") or str(t)
            normalised.append({"day": int(day), "description": str(desc).strip()})
        parsed["tasks"] = normalised
        return parsed

    for attempt in range(3):
        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return _parse(raw_text)
        except Exception as e:
            print(f"[roadmap] ⚠️ Parse attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                data = call_gemini(prompt, response_mime_type="application/json")
                if "error" in data:
                    break

    print("[roadmap] ❌ All parse attempts failed — using offline fallback")
    return _generate_fallback_plan(
        weak_topics, duration_days,
        profile["avg_score"], profile["weak_tags"], topic
    )


# ─── Monthly Limit Helper ─────────────────────────────────────────────────────

def _count_plans_this_month(roll: str) -> int:
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    result = (
        supabase.table("study_plans")
        .select("id")
        .eq("user_id", roll)
        .gte("created_at", start_of_month)
        .execute()
    )
    return len(result.data) if result.data else 0


def _has_active_plan(roll: str) -> bool:
    result = (
        supabase.table("study_plans")
        .select("id")
        .eq("user_id", roll)
        .eq("is_active", True)
        .execute()
    )
    return bool(result.data)


def _is_plan_complete(plan_id: str) -> bool:
    result = (
        supabase.table("plan_tasks")
        .select("status")
        .eq("plan_id", plan_id)
        .execute()
    )
    if not result.data:
        return False
    return all(t["status"] == "completed" for t in result.data)


# ─── API Routes ──────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    student_roll: str
    duration_days: int = 7
    topic: str = ""

@router.post("/generate")
def generate_plan(req: GenerateRequest, user: dict = Depends(get_current_user)):
    """
    Generate a new AI study plan.
    - Max 3 plans per month
    - Cannot generate if an active plan is not yet completed
    """
    _check_db()
    roll = req.student_roll.upper().strip()
    
    # Security check
    verify_student_roll(roll, user)
    if not roll:
        raise HTTPException(status_code=400, detail="student_roll is required")
        
    if not re.match(r"^[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{4}$", roll):
        raise HTTPException(status_code=422, detail="Invalid roll number format. Expected format: 22A91A0501")
        
    if req.duration_days not in VALID_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"duration_days must be one of {VALID_DURATIONS}"
        )

    # Check: active plan must be completed before making a new one
    active_res = (
        supabase.table("study_plans")
        .select("id, title")
        .eq("user_id", roll)
        .eq("is_active", True)
        .execute()
    )
    if active_res.data:
        active_plan = active_res.data[0]
        if not _is_plan_complete(active_plan["id"]):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"You have an active plan in progress: \"{active_plan['title']}\". "
                    f"Complete all tasks in your current plan before generating a new one."
                )
            )

    # Check monthly limit
    count = _count_plans_this_month(roll)
    if count >= MAX_PLANS_PER_MONTH:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly plan limit reached ({count}/{MAX_PLANS_PER_MONTH}). New plans available next month."
        )

    # Generate plan (Gemini or fallback)
    plan_data = _generate_plan_with_gemini(roll, req.duration_days, req.topic)

    # Insert plan (not active yet — student activates it)
    plan_res = (
        supabase.table("study_plans")
        .insert({
            "user_id": roll,
            "title": plan_data["title"],
            "duration_days": req.duration_days,
            "is_active": False,
        })
        .execute()
    )
    plan_id = plan_res.data[0]["id"]

    # Insert tasks
    tasks_to_insert = [
        {"plan_id": plan_id, "day_number": t["day"], "description": t["description"], "status": "pending"}
        for t in plan_data["tasks"]
    ]
    supabase.table("plan_tasks").insert(tasks_to_insert).execute()

    return {
        "success": True,
        "plan_id": plan_id,
        "title": plan_data["title"],
        "duration_days": req.duration_days,
        "tasks_count": len(tasks_to_insert),
        "plans_used_this_month": count + 1,
        "plans_remaining_this_month": MAX_PLANS_PER_MONTH - (count + 1),
    }


@router.get("/plans/{roll}")
def list_plans(roll: str, user: dict = Depends(get_current_user)):
    """List all study plans for a student, newest first."""
    _check_db()
    roll = roll.upper().strip()
    
    # Security check
    verify_student_roll(roll, user)
    result = (
        supabase.table("study_plans")
        .select("*, plan_tasks(id, day_number, description, status)")
        .eq("user_id", roll)
        .order("created_at", desc=True)
        .execute()
    )
    plans_used = _count_plans_this_month(roll)
    return {
        "roll": roll,
        "plans": result.data,
        "plans_used_this_month": plans_used,
        "plans_remaining_this_month": max(0, MAX_PLANS_PER_MONTH - plans_used),
    }


@router.patch("/plans/{plan_id}/activate")
def activate_plan(plan_id: str, user: dict = Depends(get_current_user)):
    """
    Set a plan as active. Deactivates all other plans for the same student.
    NOTE: Cannot activate if another plan is still in progress (not completed).
    """
    _check_db()
    plan_res = (
        supabase.table("study_plans")
        .select("user_id, is_active")
        .eq("id", plan_id)
        .execute()
    )
    if not plan_res.data:
        raise HTTPException(status_code=404, detail="Plan not found")

    roll = plan_res.data[0]["user_id"]

    # Security: verify the requesting user owns this plan
    verify_student_roll(roll, user)

    # Check if there's already an active incomplete plan
    active_res = (
        supabase.table("study_plans")
        .select("id, title")
        .eq("user_id", roll)
        .eq("is_active", True)
        .execute()
    )
    if active_res.data:
        active = active_res.data[0]
        if active["id"] != plan_id and not _is_plan_complete(active["id"]):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot activate — you have an active plan in progress: \"{active['title']}\". "
                    f"Complete it first."
                )
            )

    # Deactivate all → activate the selected one
    supabase.table("study_plans").update({"is_active": False}).eq("user_id", roll).execute()
    supabase.table("study_plans").update({"is_active": True}).eq("id", plan_id).execute()

    return {"success": True, "active_plan_id": plan_id}


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str, user: dict = Depends(get_current_user)):
    """Mark a task as completed."""
    _check_db()

    # Security: fetch the task's plan_id, then verify user owns that plan
    task_res = (
        supabase.table("plan_tasks")
        .select("plan_id")
        .eq("id", task_id)
        .execute()
    )
    if not task_res.data:
        raise HTTPException(status_code=404, detail="Task not found")

    plan_id = task_res.data[0]["plan_id"]
    plan_res = (
        supabase.table("study_plans")
        .select("user_id")
        .eq("id", plan_id)
        .execute()
    )
    if plan_res.data:
        roll = plan_res.data[0]["user_id"]
        verify_student_roll(roll, user)

    # Mark the task as completed
    result = (
        supabase.table("plan_tasks")
        .update({"status": "completed"})
        .eq("id", task_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task_id": task_id, "status": "completed"}


@router.get("/active/{roll}")
def get_active_plan(roll: str, user: dict = Depends(get_current_user)):
    """Return the active plan with all tasks, highlighting today's task."""
    _check_db()
    roll = roll.upper().strip()
    
    # Security check
    verify_student_roll(roll, user)
    plan_res = (
        supabase.table("study_plans")
        .select("*, plan_tasks(id, day_number, description, status)")
        .eq("user_id", roll)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    if not plan_res.data:
        return {"active_plan": None, "today_task": None, "today_day": None}

    plan = plan_res.data[0]
    tasks = sorted(plan.get("plan_tasks", []), key=lambda t: t["day_number"])

    plan_created = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
    today_utc = datetime.now(timezone.utc)
    days_elapsed = (today_utc - plan_created).days + 1
    today_day = min(days_elapsed, plan["duration_days"])
    today_task = next((t for t in tasks if t["day_number"] == today_day), None)

    return {
        "active_plan": {**plan, "plan_tasks": tasks},
        "today_day": today_day,
        "today_task": today_task,
        "is_complete": all(t["status"] == "completed" for t in tasks),
    }
