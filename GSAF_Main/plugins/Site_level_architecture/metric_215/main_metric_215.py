"""
Factor 215

Terms of Service & Privacy Pages
"""

from models.metric_result import MetricResult
from utils.keywords import PRIVACY_KEYWORDS, TERMS_KEYWORDS


def run(site_data):
    result = MetricResult(factor="215 - Terms of Service & Privacy Pages")

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

        privacy_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in PRIVACY_KEYWORDS
        ) or any(keyword in raw_html for keyword in PRIVACY_KEYWORDS)
        terms_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in TERMS_KEYWORDS
        ) or any(keyword in raw_html for keyword in TERMS_KEYWORDS)

        score = 0
        if privacy_found:
            score += 50
        if terms_found:
            score += 50

        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["privacy_page_found"] = privacy_found
        result.details["terms_page_found"] = terms_found
        result.details["links_checked"] = len(links)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
