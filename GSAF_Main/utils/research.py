import re


STUDY_KEYWORDS = [
    "study",
    "survey",
    "report",
    "research",
    "whitepaper",
    "paper",
    "analysis",
    "benchmark",
    "case study"
]

CITATION_PHRASES = [
    "according to",
    "published by",
    "conducted by",
    "reported by",
    "research from",
    "study by",
    "survey by"
]

ORGANIZATIONS = [
    "google",
    "microsoft",
    "amazon",
    "aws",
    "gartner",
    "forrester",
    "stanford",
    "harvard",
    "mit",
    "ibm",
    "oracle",
    "openai",
    "meta",
    "accenture",
    "deloitte",
    "mckinsey",
    "world bank",
    "who",
    "unesco",
    "nasa"
]

YEAR_PATTERN = r"\b(?:19\d{2}|20\d{2}|21\d{2})\b"


def analyze_research(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    study_count = sum(
        lower_text.count(word)
        for word in STUDY_KEYWORDS
    )

    citation_count = sum(
        lower_text.count(phrase)
        for phrase in CITATION_PHRASES
    )

    organization_count = sum(
        lower_text.count(org)
        for org in ORGANIZATIONS
    )

    publication_years = len(
        re.findall(YEAR_PATTERN, text)
    )

    score = 0

    score += min(study_count, 6) * 5
    score += min(citation_count, 4) * 5
    score += min(organization_count, 6) * 5
    score += min(publication_years, 4) * 5

    score = min(score, 100)

    details = {
        "study_keywords": study_count,
        "citation_phrases": citation_count,
        "organizations": organization_count,
        "publication_years": publication_years
    }

    recommendations = []

    if study_count == 0:
        recommendations.append(
            "Reference credible studies or research reports."
        )

    if organization_count == 0:
        recommendations.append(
            "Mention trusted organizations or institutions."
        )

    if publication_years == 0:
        recommendations.append(
            "Include publication years to improve credibility."
        )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }