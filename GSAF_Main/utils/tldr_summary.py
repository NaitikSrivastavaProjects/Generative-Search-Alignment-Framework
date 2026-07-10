import re


TLDR_PATTERNS = [
    "tl;dr",
    "summary",
    "quick summary",
    "in short",
    "key takeaways",
    "at a glance",
    "overview",
    "executive summary"
]


def analyze_tldr_summary(site_data):

    soup = site_data.soup

    text = soup.get_text(" ", strip=True)

    lower_text = text.lower()

    score = 100

    recommendations = []

    details = {
        "summary_found": False,
        "summary_position": "Not Found",
        "matched_pattern": None
    }

    body_text = lower_text[:2500]

    for pattern in TLDR_PATTERNS:

        index = body_text.find(pattern)

        if index != -1:

            details["summary_found"] = True
            details["matched_pattern"] = pattern

            if index < 800:

                details["summary_position"] = "Top"

            elif index < 1600:

                details["summary_position"] = "Middle"

                score -= 20

                recommendations.append(
                    "Move the summary section closer to the top of the page."
                )

            else:

                details["summary_position"] = "Bottom"

                score -= 40

                recommendations.append(
                    "Place the TL;DR or summary near the beginning of the content."
                )

            break

    if not details["summary_found"]:

        score = 30

        recommendations.append(
            "Add a TL;DR or short summary at the beginning of the page."
        )

    score = max(0, min(score, 100))

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }