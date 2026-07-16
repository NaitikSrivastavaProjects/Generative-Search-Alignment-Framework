"""
Factor 221

User Reviews / Site Reputation
"""

from models.metric_result import MetricResult
from utils.helpers import get_link_targets


def run(site_data):
    result = MetricResult(factor="221 - Site Reputation")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        links = get_link_targets(soup, getattr(site_data, 'url', ''))

        reputation_found = any(
            "trustpilot" in link["href"].lower() or "bbb" in link["href"].lower() or "review" in link["text"].lower()
            for link in links
        )
        score = 100 if reputation_found else 0
        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["reputation_links_found"] = reputation_found
        result.details["links_checked"] = len(links)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
