import re


IMPORTANT_PHRASES = [
    "important",
    "key",
    "critical",
    "essential",
    "must",
    "should",
    "best practice",
    "recommended",
    "warning",
    "note",
    "tip",
    "remember",
    "takeaway",
    "summary"
]


def analyze_bold_key_phrases(site_data):

    soup = site_data.soup

    bold_tags = soup.find_all(
        ["b", "strong"]
    )

    bold_text = " ".join(
        tag.get_text(" ", strip=True)
        for tag in bold_tags
    ).lower()

    highlighted_phrases = 0

    for phrase in IMPORTANT_PHRASES:

        highlighted_phrases += bold_text.count(
            phrase
        )

    score = 0

    score += min(
        len(bold_tags),
        15
    ) * 4

    score += min(
        highlighted_phrases,
        10
    ) * 4

    score = min(score, 100)

    details = {
        "bold_elements": len(bold_tags),
        "important_phrases_highlighted": highlighted_phrases
    }

    recommendations = []

    if score < 75:

        if len(bold_tags) == 0:
            recommendations.append(
                "Highlight important information using <strong> or <b> tags."
            )

        if highlighted_phrases < 3:
            recommendations.append(
                "Bold key insights, recommendations and important phrases."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }