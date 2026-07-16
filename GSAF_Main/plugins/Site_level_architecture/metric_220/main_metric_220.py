"""
Factor 220

Site Usability
"""

from models.metric_result import MetricResult
from utils.helpers import get_link_targets


def run(site_data):
    result = MetricResult(factor="220 - Site Usability")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        links = get_link_targets(soup, getattr(site_data, 'url', ''))

        nav_links = [link for link in links if len(link["text"].split()) <= 3]
        score = 70 if nav_links else 30
        result.score = score
        result.status = "Found" if score >= 70 else "Partial" if score > 0 else "Not Found"
        result.details["navigation_links_found"] = len(nav_links)
        result.details["total_links_found"] = len(links)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
