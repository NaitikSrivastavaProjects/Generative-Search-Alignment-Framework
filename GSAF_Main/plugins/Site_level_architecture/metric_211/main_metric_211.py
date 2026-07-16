"""
Factor 98

Sitemap Availability
"""

from models.metric_result import MetricResult
from utils.keywords import SITEMAP_KEYWORDS


def run(site_data):
    result = MetricResult(factor="211 - Sitemap Availability")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(" ", strip=True)
            links.append({"href": href, "text": text})

        sitemap_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in SITEMAP_KEYWORDS
        ) or any(keyword in raw_html for keyword in SITEMAP_KEYWORDS)

        score = 100 if sitemap_found else 0
        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["sitemap_found"] = sitemap_found
        result.details["links_checked"] = len(links)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
