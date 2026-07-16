"""
Factor 217

Breadcrumb Navigation
"""

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="217 - Breadcrumb Navigation")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        breadcrumb = soup.find(class_="breadcrumb") or soup.find("nav", attrs={"aria-label": "breadcrumb"})
        score = 100 if breadcrumb else 0
        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["breadcrumb_found"] = bool(breadcrumb)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
