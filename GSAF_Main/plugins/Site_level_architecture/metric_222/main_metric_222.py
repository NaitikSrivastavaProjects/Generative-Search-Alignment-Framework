"""
Factor 222

Google Analytics & Search Console
"""

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="222 - Google Analytics & Search Console")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        analytics_found = False
        search_console_found = False
        for tag in soup.find_all(["meta", "script", "link"]):
            attrs = " ".join(str(tag.attrs).lower() for tag in [tag])
            if "googletagmanager" in attrs or "gtag" in attrs:
                analytics_found = True
            if "google-site-verification" in attrs or "search-console" in attrs:
                search_console_found = True

        score = 100 if analytics_found and search_console_found else 70 if analytics_found or search_console_found else 0
        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["google_analytics_found"] = analytics_found
        result.details["google_search_console_found"] = search_console_found
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
