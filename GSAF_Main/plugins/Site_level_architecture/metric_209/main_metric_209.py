"""
Factor 95

Domain Trust
"""

from urllib.parse import urlparse

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="209 - Domain Trust")

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

        domain = urlparse(page_url).netloc.lower()
        response_url = getattr(response, 'url', page_url)
        secure = str(response_url).startswith("https") or page_url.lower().startswith("https://")
        score = 70 if secure and len(domain) > 5 else 40 if domain else 0

        result.score = score
        result.status = "Found" if score >= 70 else "Partial" if score > 0 else "Not Found"
        result.details["domain"] = domain
        result.details["https_enabled"] = secure
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
