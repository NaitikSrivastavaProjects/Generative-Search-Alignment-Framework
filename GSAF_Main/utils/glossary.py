import re


DEFINITION_PATTERNS = [
    r"\bis defined as\b",
    r"\brefers to\b",
    r"\bis a\b",
    r"\bis an\b",
    r"\bmeans\b",
    r"\bknown as\b",
    r"\bdescribes\b"
]


def analyze_glossary(site_data):

    soup = site_data.soup

    text = soup.get_text(" ", strip=True)

    lower_text = text.lower()

    definition_patterns = 0

    for pattern in DEFINITION_PATTERNS:

        definition_patterns += len(
            re.findall(pattern, lower_text)
        )

    headings = soup.find_all(
        ["h2", "h3", "dt"]
    )

    glossary_sections = 0

    for heading in headings:

        heading_text = heading.get_text(
            " ",
            strip=True
        ).lower()

        if any(
            word in heading_text
            for word in [
                "glossary",
                "terminology",
                "definitions",
                "terms",
                "dictionary"
            ]
        ):

            glossary_sections += 1

    bold_terms = len(
        soup.find_all(["strong", "b"])
    )

    score = 0

    score += min(definition_patterns, 8) * 8
    score += min(glossary_sections, 2) * 20
    score += min(bold_terms, 15) * 2

    score = min(score, 100)

    details = {
        "definition_patterns": definition_patterns,
        "glossary_sections": glossary_sections,
        "highlighted_terms": bold_terms
    }

    recommendations = []

    if score < 75:

        if glossary_sections == 0:

            recommendations.append(
                "Create a glossary or terminology section for important concepts."
            )

        if definition_patterns < 3:

            recommendations.append(
                "Clearly define important terms using simple language."
            )

        if bold_terms < 5:

            recommendations.append(
                "Highlight important terms before explaining them."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }