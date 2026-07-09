import re


STRONG_WORDS = [
    "always",
    "never",
    "best",
    "worst",
    "important",
    "critical",
    "essential",
    "key",
    "must",
    "should",
    "avoid",
    "improve",
    "increase",
    "reduce",
    "optimize",
    "security",
    "performance",
    "quality",
    "automation",
    "scalable"
]


def analyze_quotable_insights(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    sentences = re.split(r"[.!?]+", text)

    quotable_sentences = 0
    strong_word_matches = 0

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        words = sentence.split()

        if len(words) > 25:
            continue

        for word in STRONG_WORDS:

            if re.search(rf"\b{re.escape(word)}\b", sentence, re.IGNORECASE):

                quotable_sentences += 1
                strong_word_matches += 1
                break

    score = 0

    score += min(quotable_sentences, 5) * 15
    score += min(strong_word_matches, 5) * 5

    if quotable_sentences >= 3:
        score += 25

    score = min(score, 100)

    details = {
        "quotable_sentences": quotable_sentences,
        "strong_word_matches": strong_word_matches
    }

    recommendations = []

    if quotable_sentences < 3:
        recommendations.append(
            "Include more short and impactful statements."
        )

    if strong_word_matches == 0:
        recommendations.append(
            "Use stronger action words to improve quotability."
        )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }