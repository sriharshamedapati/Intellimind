"""
recommender.py — Study Recommendations
========================================
Generates targeted study recommendations based on detected weaknesses.
"""

TOPIC_RESOURCES = {
    "arrays": "Practice 10 problems on Arrays (sliding window, two-pointer techniques)",
    "linked lists": "Implement singly and doubly linked lists, solve 3 reversal problems",
    "trees": "Study BST operations and implement inorder/preorder/postorder traversals",
    "graphs": "Practice BFS and DFS algorithms, solve connected components problems",
    "dynamic programming": "Solve basic DP problems (Fibonacci, coin change, 0/1 knapsack)",
    "recursion": "Practice recursive algorithms and backtracking (N-Queens, subsets)",
    "sorting": "Review quicksort, mergesort, and analyze their time/space complexities",
    "searching": "Practice binary search variations (rotated array, search range)",
    "oop": "Review Object-Oriented Programming concepts (inheritance, polymorphism, encapsulation)",
    "sql": "Practice SQL queries with JOINS, GROUP BY, and subqueries",
    "os concepts": "Study Operating System concepts (process scheduling, memory management, deadlocks)",
    "system design": "Review basics of scalable architectures (load balancing, caching, sharding)",
    "networks": "Study OSI and TCP/IP models, routing protocols, and IP subnetting",
    "aptitude": "Take a 60-minute mock test on quantitative and logical reasoning",
    "lsrw": "Practice LSRW skills (Listening, Speaking, Reading, Writing) using English exercises",
    # Legacy fallbacks from old implementation
    "loop": "Practice 10 problems on Python loops (for, while, nested loops)",
    "syntax": "Revise Python syntax rules (indentation, colons, blocks)",
    "range": "Understand range() function with examples and edge cases",
    "function": "Study function calls with simple programs and dry runs",
    "control flow": "Practice control flow problems (loops + conditions combined)",
}

def generate_recommendations(summary_data: dict) -> list[str]:
    """Generate study recommendations from weakness data."""
    weaknesses = summary_data.get("weaknesses", [])
    recommendations = []

    for w in weaknesses:
        w_lower = w.lower()
        matched = False
        
        # 1. Exact or substring match against predefined dictionary
        for key, resource in TOPIC_RESOURCES.items():
            if key in w_lower or w_lower in key:
                recommendations.append(resource)
                matched = True
                break
                
        # 2. Fallback
        if not matched:
            recommendations.append(f"Improve understanding of: {w}")

    return list(set(recommendations))