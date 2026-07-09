import re


EXPERT_TITLES = [
    "dr",
    "professor",
    "prof",
    "expert",
    "researcher",
    "scientist",
    "analyst",
    "engineer",
    "founder",
    "ceo"
]

QUOTE_INDICATORS = [
    "according to",
    "states",
    "said",
    "mentions",
    "writes",
    "explains",
    "reported",
    "claims"
]


def analyze_expert_quotes(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    expert_titles = sum(
        lower_text.count(word)
        for word in EXPERT_TITLES
    )

    quote_indicators = sum(
        lower_text.count(word)
        for word in QUOTE_INDICATORS
    )

    quoted_statements = len(
        re.findall(r'"(.*?)"', site_data.html)
    )

    score = 0

    score += min(expert_titles, 4) * 10
    score += min(quote_indicators, 4) * 10
    score += min(quoted_statements, 3) * 20

    if quoted_statements > 0 and quote_indicators > 0:
        score += 20

    score = min(score, 100)

    details = {
        "expert_titles": expert_titles,
        "quote_indicators": quote_indicators,
        "quoted_statements": quoted_statements
    }

    recommendations = []

    if expert_titles == 0:
        recommendations.append(
            "Reference recognised experts or professionals."
        )

    if quoted_statements == 0:
        recommendations.append(
            "Include direct expert quotations where appropriate."
        )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }