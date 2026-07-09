import re


STATISTICAL_KEYWORDS = [
    "average",
    "median",
    "mean",
    "growth",
    "increase",
    "decrease",
    "variance",
    "distribution",
    "sample",
    "survey",
    "dataset",
    "statistics",
    "ratio",
    "percentage"
]


NUMBER_PATTERN = r"\b\d+(?:,\d{3})*(?:\.\d+)?\b"

PERCENTAGE_PATTERN = r"\b\d+(?:\.\d+)?%"

CURRENCY_PATTERN = (
    r"(?:₹|\$|€|£)\s?\d+(?:,\d{3})*(?:\.\d+)?"
)

YEAR_PATTERN = r"\b(?:19\d{2}|20\d{2}|21\d{2})\b"

MEASUREMENT_PATTERN = (
    r"\b\d+(?:\.\d+)?\s?"
    r"(?:GB|MB|TB|KB|kg|g|mg|km|m|cm|mm|ms|s|hrs|hours|minutes|%)\b"
)


def analyze_statistics(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    numbers = re.findall(NUMBER_PATTERN, text)

    percentages = re.findall(PERCENTAGE_PATTERN, text)

    currency = re.findall(CURRENCY_PATTERN, text)

    years = re.findall(YEAR_PATTERN, text)

    measurements = re.findall(MEASUREMENT_PATTERN, text)

    keyword_count = sum(
        lower_text.count(word)
        for word in STATISTICAL_KEYWORDS
    )

    score = 0

    score += min(len(numbers), 10) * 2
    score += min(len(percentages), 3) * 5
    score += min(len(currency), 3) * 5
    score += min(len(years), 3) * 5
    score += min(len(measurements), 4) * 5
    score += min(keyword_count, 5) * 3

    score = min(score, 100)

    details = {
        "numbers": len(numbers),
        "percentages": len(percentages),
        "currency": len(currency),
        "years": len(years),
        "measurements": len(measurements),
        "statistical_keywords": keyword_count
    }

    recommendations = []

    if len(numbers) < 5:
        recommendations.append(
            "Include more quantitative facts and figures."
        )

    if len(percentages) == 0:
        recommendations.append(
            "Add percentages where appropriate."
        )

    if len(years) == 0:
        recommendations.append(
            "Mention publication years or recent data."
        )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }