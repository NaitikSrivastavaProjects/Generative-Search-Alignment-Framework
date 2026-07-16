"""
Factor 218

Mobile Optimization
"""

from models.metric_result import MetricResult
from utils.helpers import extract_text


def run(site_data):
    result = MetricResult(factor="218 - Mobile Optimization")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        viewport = soup.find("meta", attrs={"name": "viewport"})
        responsive_score = 50 if viewport else 0
        text = extract_text(soup)
        has_content = bool(text.strip())

        score = responsive_score + (50 if has_content else 0)
        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["viewport_meta_found"] = bool(viewport)
        result.details["has_content"] = has_content
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
