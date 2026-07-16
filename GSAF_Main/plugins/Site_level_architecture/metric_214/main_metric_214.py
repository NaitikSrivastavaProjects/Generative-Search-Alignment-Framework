"""
Factor 214

SSL Certificate / HTTPS
"""

from models.metric_result import MetricResult
from utils.url_utils import URLUtils


def run(site_data):
    result = MetricResult(factor="214 - SSL Certificate")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        page_url = getattr(site_data, 'url', '')
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        response = getattr(site_data, 'response', None)
        response_url = getattr(response, 'url', page_url)
        https_enabled = URLUtils.is_https(page_url) or str(response_url).startswith("https")
        score = 100 if https_enabled else 0

        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["https_enabled"] = https_enabled
        result.details["final_url"] = response_url
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
