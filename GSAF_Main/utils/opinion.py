OPINION_WORDS = [
    "best",
    "worst",
    "always",
    "never",
    "must",
    "should",
    "recommend",
    "essential",
    "critical",
    "important",
    "avoid",
    "prefer",
    "better",
    "superior",
    "inferior",
    "key",
    "necessary"
]

COMPARISON_PHRASES = [
    "better than",
    "worse than",
    "compared to",
    "instead of",
    "rather than",
    "more effective",
    "less effective"
]

RECOMMENDATION_PHRASES = [
    "we recommend",
    "you should",
    "it is recommended",
    "best practice",
    "our recommendation"
]


def analyze_opinions(site_data):

    text = site_data.soup.get_text(" ", strip=True).lower()

    opinion_words = sum(text.count(word) for word in OPINION_WORDS)

    comparison_phrases = sum(
        text.count(phrase)
        for phrase in COMPARISON_PHRASES
    )

    recommendation_phrases = sum(
        text.count(phrase)
        for phrase in RECOMMENDATION_PHRASES
    )

    score = 0

    score += min(opinion_words, 10) * 3
    score += min(comparison_phrases, 5) * 8
    score += min(recommendation_phrases, 5) * 8

    score = min(score, 100)

    details = {
        "opinion_words": opinion_words,
        "comparison_phrases": comparison_phrases,
        "recommendation_phrases": recommendation_phrases
    }

    recommendations = []

    if comparison_phrases == 0:
        recommendations.append(
            "Include comparisons to strengthen opinions."
        )

    if recommendation_phrases == 0:
        recommendations.append(
            "Add actionable recommendations."
        )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }