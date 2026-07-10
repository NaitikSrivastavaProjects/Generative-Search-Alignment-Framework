import re


DEFINITION_PATTERNS = [
    r"\bis defined as\b",
    r"\brefers to\b",
    r"\bis a\b",
    r"\bare\b",
    r"\bmeans\b",
    r"\bcan be defined as\b",
    r"\bis known as\b",
    r"\bin simple terms\b",
    r"\bin other words\b"
]


def analyze_definition_blocks(site_data):

    soup = site_data.soup

    text = soup.get_text(" ", strip=True)

    lower_text = text.lower()

    definition_count = 0

    for pattern in DEFINITION_PATTERNS:

        definition_count += len(
            re.findall(pattern, lower_text)
        )

    paragraphs = soup.find_all("p")

    short_paragraphs = 0

    for paragraph in paragraphs:

        words = len(
            paragraph.get_text(
                " ",
                strip=True
            ).split()
        )

        if 10 <= words <= 60:

            short_paragraphs += 1

    score = 0

    score += min(definition_count, 8) * 10
    score += min(short_paragraphs, 10) * 2

    score = min(score, 100)

    details = {
        "definition_patterns": definition_count,
        "definition_blocks": short_paragraphs
    }

    recommendations = []

    if score < 75:

        if definition_count == 0:

            recommendations.append(
                "Include definition statements such as 'X is defined as...' or 'X refers to...'."
            )

        if short_paragraphs < 3:

            recommendations.append(
                "Present important concepts in short standalone definition blocks."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }