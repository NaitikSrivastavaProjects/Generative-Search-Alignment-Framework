"""
Factor 208

Site Architecture
"""

from urllib.parse import urlparse

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="208 - Site Architecture")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        page_url = getattr(site_data, 'url', '')
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href:
                links.append({"href": href, "text": link.get_text(" ", strip=True)})

        internal_links = []
        base_parsed = urlparse(page_url)
        for link in links:
            href = link["href"]
            parsed_href = urlparse(href)
            if not parsed_href.scheme and not parsed_href.netloc:
                internal_links.append(link)
            elif parsed_href.scheme in ("http", "https") and parsed_href.netloc == base_parsed.netloc:
                internal_links.append(link)

        score = 100 if len(internal_links) >= 5 else 50 if internal_links else 0
        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["internal_links_found"] = len(internal_links)
        result.details["total_links_found"] = len(links)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
