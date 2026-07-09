import re


CONTRARIAN_PHRASES = [
    "contrary to popular belief",
    "common misconception",
    "myth",
    "however",
    "although",
    "despite",
    "instead",
    "in reality",
    "the truth is",
    "most people think",
    "many believe",
    "widely believed",
    "popular opinion",
    "conventional wisdom"
]

EVIDENCE_PHRASES = [
    "because",
    "based on",
    "according to",
    "research",
    "study",
    "data",
    "evidence",
    "results",
    "analysis",
    "experiment"
]


def analyze_counter_conventional(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    contrarian_count = sum(
        lower_text.count(item)
        for item in CONTRARIAN_PHRASES
    )

    evidence_count = sum(
        lower_text.count(item)
        for item in EVIDENCE_PHRASES
    )

    score = 0

    score += min(contrarian_count, 6) * 10
    score += min(evidence_count, 8) * 5

    score = min(score, 100)

    details = {
        "contrarian_phrases": contrarian_count,
        "supporting_evidence": evidence_count
    }

    recommendations = []

    if score < 75:

        if contrarian_count == 0:
            recommendations.append(
                "Challenge common assumptions where supported by evidence."
            )

        if evidence_count < 3:
            recommendations.append(
                "Support alternative viewpoints with credible evidence."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }