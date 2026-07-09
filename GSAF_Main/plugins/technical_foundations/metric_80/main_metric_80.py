from models.metric_result import MetricResult
from utils.helpers import get_status


CSR_ROOT_PATTERNS = ["id=\"root\"", "id=\"app\"", "id='root'", "id='app'"]


def run(site_data):
    result = MetricResult(factor="80 - Server-Side Rendering")

    try:
        soup = site_data.soup
        html = site_data.html

        paragraphs = soup.find_all("p")
        word_count = sum(len(p.get_text().split()) for p in paragraphs)

        has_csr_root = any(pattern in html for pattern in CSR_ROOT_PATTERNS)

        result.details["raw_word_count"] = word_count
        result.details["csr_root_div_detected"] = has_csr_root

        if word_count >= 500:
            result.score = 100
        elif word_count >= 200:
            result.score = 60
        elif word_count >= 50:
            result.score = 30
        else:
            result.score = 0

        if has_csr_root and word_count < 50:
            result.score = 0
            result.details["rendering"] = "Client-Side Rendered"
            result.recommendations.append(
                "Page appears to be client-side rendered (empty root div detected). "
                "Switch to server-side rendering so crawlers can access content directly."
            )
        elif word_count >= 500:
            result.details["rendering"] = "Server-Side Rendered"
        else:
            result.details["rendering"] = "Partial or Unknown"
            result.recommendations.append(
                "Low content in raw HTML — page may be partially client-side rendered. "
                "Ensure main content is present in initial HTML response."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()