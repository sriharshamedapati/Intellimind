"""
recommender.py — Study Recommendations
========================================
Generates targeted study recommendations based on detected weaknesses.
"""


def generate_recommendations(summary_data: dict) -> list[str]:
    """Generate study recommendations from weakness data."""
    weaknesses = summary_data.get("weaknesses", [])
    recommendations = []

    for w in weaknesses:
        w_lower = w.lower()

        if "loop" in w_lower:
            recommendations.append(
                "Practice 10 problems on Python loops (for, while, nested loops)"
            )
        elif "syntax" in w_lower or "indentation" in w_lower:
            recommendations.append(
                "Revise Python syntax rules (indentation, colons, blocks)"
            )
        elif "range" in w_lower:
            recommendations.append(
                "Understand range() function with examples and edge cases"
            )
        elif "function" in w_lower and "java" in w_lower:
            recommendations.append(
                "Study Java function calls with simple programs and dry runs"
            )
        elif "control flow" in w_lower:
            recommendations.append(
                "Practice control flow problems (loops + conditions combined)"
            )
        else:
            recommendations.append(f"Improve understanding of: {w}")

    return list(set(recommendations))