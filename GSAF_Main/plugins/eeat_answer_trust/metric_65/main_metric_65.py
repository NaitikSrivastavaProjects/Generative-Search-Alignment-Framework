import re
from models.metric_result import MetricResult
from utils.helpers import get_status


ORIGINALITY_PHRASES = [
    "our study", "our research", "we found", "we surveyed",
    "our data shows", "according to our", "in our analysis",
    "proprietary data", "our survey of", "we analyzed",
    "our findings", "we conducted"
]

STAT_PATTERN = re.compile(
    r'\b\d+\.?\d*\s*(%|percent|respondents|participants|users|people surveyed)\b',
    re.IGNORECASE
)


def run(site_data):
    result = MetricResult(factor="65 - Original Research and Data")

    try:
        soup = site_data.soup
        text = soup.get_text().lower()

        signals_found = [phrase for phrase in ORIGINALITY_PHRASES if phrase in text]
        stat_matches = STAT_PATTERN.findall(soup.get_text())

        result.details["originality_phrases_found"] = signals_found
        result.details["statistics_found"] = stat_matches[:5]

        if len(signals_found) >= 3 and stat_matches:
            base_score = 80
        elif signals_found and stat_matches:
            base_score = 60
        elif signals_found or stat_matches:
            base_score = 40
        else:
            base_score = 10

        ai_data = site_data.ai_results.get("metric_65", {})
        if ai_data:
            originality = ai_data.get("originality", "").lower()
            result.details["ai_originality_rating"] = originality
            result.details["ai_reasoning"] = ai_data.get("reasoning", "")
            originality_bonus = {"high": 20, "medium": 10, "low": 0}.get(originality, 0)
            result.score = min(100, base_score + originality_bonus)
        else:
            result.score = base_score

        result.status = get_status(result.score)

        if not signals_found and not stat_matches:
            result.recommendations.append(
                "No original research signals detected. "
                "Adding proprietary data, surveys, or first-hand findings significantly "
                "improves AI answer engine citation likelihood."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()