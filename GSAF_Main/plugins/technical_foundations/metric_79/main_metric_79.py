from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import CALCULATOR_CLASS_KEYWORDS


HIDDEN_CONTENT_PATTERNS = [
    "accordion", "collapse", "tab-content",
    "toggle", "expandable", "dropdown-content"
]


def run(site_data):
    result = MetricResult(factor="79 - Crawlability of Answer Blocks")

    try:
        soup = site_data.soup

        paragraphs = soup.find_all("p")
        word_count = sum(len(p.get_text().split()) for p in paragraphs)

        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        hidden_patterns = soup.find_all(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in HIDDEN_CONTENT_PATTERNS)
        )

        result.details["raw_word_count"] = word_count
        result.details["headings_in_raw_html"] = len(headings)
        result.details["hidden_content_patterns_found"] = len(hidden_patterns)

        if word_count >= 500:
            result.score = 100
        elif word_count >= 200:
            result.score = 70
        elif word_count >= 50:
            result.score = 40
        else:
            result.score = 10

        if hidden_patterns and word_count < 300:
            result.score = max(0, result.score - 20)
            result.recommendations.append(
                "Content appears to be hidden behind accordion or tab elements. "
                "Ensure answer content is present in raw HTML for crawler access."
            )

        if len(headings) == 0:
            result.recommendations.append(
                "No headings found in raw HTML — answer blocks may not be crawlable."
            )

        result.status = get_status(result.score)
        result.details["note"] = (
            "Full crawlability check requires a browser renderer. "
            "This is a proxy check based on raw HTML content."
        )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()