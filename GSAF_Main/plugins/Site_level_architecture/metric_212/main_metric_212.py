"""
Factor 212

Site Uptime
"""

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="212 - Site Uptime")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        response = getattr(site_data, 'response', None)
        status_code = getattr(response, 'status_code', 0) if response is not None else 0
        score = 100 if status_code < 400 else 0

        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["status_code"] = status_code
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
