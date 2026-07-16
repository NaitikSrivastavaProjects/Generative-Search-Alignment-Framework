"""
Factor 97

Site Updates / Maintenance
"""

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="210 - Site Updates")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        response = getattr(site_data, 'response', None)

        last_modified_header = ""
        status_code = 0
        if response is not None:
            headers = getattr(response, 'headers', {})
            if hasattr(headers, 'get'):
                last_modified_header = headers.get("last-modified", "")
            status_code = getattr(response, 'status_code', 0)

        score = 100 if last_modified_header else 50
        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["last_modified_header"] = last_modified_header
        result.details["status_code"] = status_code
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
