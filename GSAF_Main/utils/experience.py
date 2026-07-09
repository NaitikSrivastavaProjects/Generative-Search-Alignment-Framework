import re


EXPERIENCE_PATTERNS = [
    r"\bwe tested\b",
    r"\bwe tried\b",
    r"\bwe implemented\b",
    r"\bwe measured\b",
    r"\bour team\b",
    r"\bwe observed\b",
    r"\bwe found\b",
    r"\bwe discovered\b",
    r"\bin our experience\b",
    r"\bfrom our experience\b",
    r"\bwe analyzed\b",
    r"\bwe built\b",
    r"\bwe compared\b"
]


TIME_PATTERNS = [
    r"\b\d+\s+days?\b",
    r"\b\d+\s+weeks?\b",
    r"\b\d+\s+months?\b",
    r"\b\d+\s+years?\b"
]


def analyze_first_hand_experience(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    experience_matches = 0

    for pattern in EXPERIENCE_PATTERNS:
        experience_matches += len(
            re.findall(pattern, lower_text)
        )

    duration_matches = 0

    for pattern in TIME_PATTERNS:
        duration_matches += len(
            re.findall(pattern, lower_text)
        )

    first_person = len(
        re.findall(r"\b(we|our|us)\b", lower_text)
    )

    score = 0

    score += min(experience_matches, 5) * 12
    score += min(duration_matches, 4) * 10
    score += min(first_person, 5) * 6

    score = min(score, 100)

    details = {
        "experience_mentions": experience_matches,
        "time_periods": duration_matches,
        "first_person_references": first_person
    }

    recommendations = []

    if score < 75:

        if experience_matches == 0:
            recommendations.append(
                "Include first-hand testing or implementation experience."
            )

        if duration_matches == 0:
            recommendations.append(
                "Mention how long the experiment or implementation was performed."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }