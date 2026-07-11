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

        title_tag = soup.find("title")
        meta_desc = soup.find("meta", attrs={"name": "description"})

        title = title_tag.get_text(strip=True) if title_tag else ""
        meta = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""

        result.details["originality_phrases_found"] = signals_found
        result.details["statistics_found"] = stat_matches[:5]
        result.details["title"] = title
        result.details["meta_description"] = meta
        result.details["ai_judgment_pending"] = True
        result.details["note"] = (
            "Rule-based originality signals extracted. "
            "AI originality judgment (High/Medium/Low) will be added via ai_batch."
        )

        if len(signals_found) >= 3 and stat_matches:
            result.score = 80
        elif signals_found and stat_matches:
            result.score = 60
        elif signals_found or stat_matches:
            result.score = 40
        else:
            result.score = 10
            result.recommendations.append(
                "No original research signals detected. "
                "Adding proprietary data, surveys, or first-hand findings significantly "
                "improves AI answer engine citation likelihood."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()