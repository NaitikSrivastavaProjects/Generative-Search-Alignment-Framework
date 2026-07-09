import re


CASE_STUDY_PATTERNS = [
    r"\bcase study\b",
    r"\bsuccess story\b",
    r"\bclient story\b",
    r"\bcustomer story\b",
    r"\breal world\b",
    r"\bwe helped\b",
    r"\bresults\b",
    r"\boutcome\b",
    r"\bimplementation\b",
    r"\bdeployment\b"
]

IMPROVEMENT_PATTERNS = [
    r"\b\d+%\b",
    r"\b\d+\s*percent\b",
    r"\b\d+\s+months?\b",
    r"\b\d+\s+weeks?\b",
    r"\b\d+\s+days?\b",
    r"\btraffic\b",
    r"\bconversion\b",
    r"\brevenue\b",
    r"\bleads\b",
    r"\bgrowth\b",
    r"\bincrease\b",
    r"\breduce\b",
    r"\bimproved\b"
]


def analyze_case_studies(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    case_studies = 0

    for pattern in CASE_STUDY_PATTERNS:
        case_studies += len(
            re.findall(pattern, lower_text)
        )

    metrics = 0

    for pattern in IMPROVEMENT_PATTERNS:
        metrics += len(
            re.findall(pattern, lower_text)
        )

    numeric_values = len(
        re.findall(r"\b\d+(?:\.\d+)?%?\b", text)
    )

    score = 0

    score += min(case_studies, 5) * 12
    score += min(metrics, 8) * 6
    score += min(numeric_values, 10) * 3

    score = min(score, 100)

    details = {
        "case_study_mentions": case_studies,
        "performance_metrics": metrics,
        "numeric_values": numeric_values
    }

    recommendations = []

    if score < 75:

        if case_studies == 0:
            recommendations.append(
                "Include real-world case studies to improve credibility."
            )

        if metrics < 2:
            recommendations.append(
                "Support case studies with measurable results like traffic, conversions or revenue."
            )

        if numeric_values < 5:
            recommendations.append(
                "Add more numerical evidence to strengthen the case study."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }