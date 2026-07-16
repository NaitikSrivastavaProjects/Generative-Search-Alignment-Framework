'''
Conversational Phrasing Checker:
Detects whether headings/content use natural spoken-language phrasing
like "how do I", "what is", "why does" — matching how users query AI.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

CONVERSATIONAL_PHRASES = (
    "how do i", "how do you", "what is", "what are", "why does",
    "why is", "can i", "can you", "how does", "how can i", "should i"
)

def run(site_data):
    result = MetricResult(factor="5 - Conversational Phrasing")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])

        if not headings:
            result.score = 0
            result.status = get_status(0)
            result.details["total_headings"] = 0
            result.recommendations.append("Add H1/H2 headings using natural spoken-language phrasing.")
            return result.to_dict()

        matched = [h.get_text(strip=True) for h in headings if any(p in h.get_text(strip=True).lower() for p in CONVERSATIONAL_PHRASES)]
        ratio = len(matched) / len(headings)
        score = round(ratio * 100)

        result.score = score
        result.status = get_status(score)
        result.details["total_headings"] = len(headings)
        result.details["conversational_headings_found"] = len(matched)
        result.details["examples"] = matched[:5]

        if not matched:
            result.recommendations.append("Rephrase headings using natural spoken language, e.g. 'How do I...', 'What is...'")
        elif ratio < 0.5:
            result.recommendations.append("Use conversational phrasing in more headings to match how users query AI assistants.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()