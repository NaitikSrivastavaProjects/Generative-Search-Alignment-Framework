from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import EDITORIAL_STRONG, EDITORIAL_MEDIUM, EDITORIAL_WEAK


def run(site_data):
    result = MetricResult(factor="66 - Editorial Review Bylines")

    try:
        soup = site_data.soup
        text = soup.get_text().lower()

        strong_found = [p for p in EDITORIAL_STRONG if p in text]
        medium_found = [p for p in EDITORIAL_MEDIUM if p in text]
        weak_found = [p for p in EDITORIAL_WEAK if p in text]

        result.details["strong_patterns_found"] = strong_found
        result.details["medium_patterns_found"] = medium_found
        result.details["weak_patterns_found"] = weak_found

        if strong_found:
            result.score = 100
        elif medium_found:
            result.score = 75
        elif weak_found:
            result.score = 50
        else:
            result.score = 0
            result.recommendations.append(
                "No editorial review byline detected. Adding a 'medically reviewed by' or "
                "'fact-checked by' byline significantly improves E-E-A-T trust signals."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()