import re


COMPARISON_PHRASES = [
    "better than",
    "worse than",
    "compared to",
    "comparison",
    "compare",
    "versus",
    "vs",
    "instead of",
    "rather than",
    "pros and cons",
    "advantages",
    "disadvantages",
    "difference between"
]

DECISION_PHRASES = [
    "best for",
    "recommended for",
    "choose",
    "ideal for",
    "works best",
    "suitable for",
    "use when",
    "avoid when",
    "preferred when",
    "wins when"
]

TABLE_TAGS = [
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td"
]


def analyze_comparison_framework(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    comparison_count = sum(
        lower_text.count(item)
        for item in COMPARISON_PHRASES
    )

    decision_count = sum(
        lower_text.count(item)
        for item in DECISION_PHRASES
    )

    table_elements = sum(
        len(site_data.soup.find_all(tag))
        for tag in TABLE_TAGS
    )

    score = 0

    score += min(comparison_count, 6) * 8
    score += min(decision_count, 5) * 8
    score += min(table_elements, 10) * 2

    score = min(score, 100)

    details = {
        "comparison_phrases": comparison_count,
        "decision_phrases": decision_count,
        "table_elements": table_elements
    }

    recommendations = []

    if score < 75:

        if comparison_count == 0:
            recommendations.append(
                "Include direct comparisons between alternatives."
            )

        if decision_count == 0:
            recommendations.append(
                "Explain when one option is better than another."
            )

        if table_elements == 0:
            recommendations.append(
                "Use comparison tables for better readability."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }