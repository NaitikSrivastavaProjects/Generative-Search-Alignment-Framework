from urllib.parse import urljoin
from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import TRANSPARENCY_PAGE_KEYWORDS


def run(site_data):
    result = MetricResult(factor="68 - Transparency Pages")

    try:
        soup = site_data.soup
        base_url = site_data.url
        all_links = soup.find_all("a", href=True)

        found_pages = {}
        missing_pages = []

        for page_type, keywords in TRANSPARENCY_PAGE_KEYWORDS.items():
            page_found = False
            for link in all_links:
                href = link["href"].lower()
                link_text = link.get_text().lower()
                if any(kw in href or kw in link_text for kw in keywords):
                    found_pages[page_type] = urljoin(base_url, link["href"])
                    page_found = True
                    break
            if not page_found:
                missing_pages.append(page_type)

        total = len(TRANSPARENCY_PAGE_KEYWORDS)
        result.details["pages_found"] = found_pages
        result.details["pages_missing"] = missing_pages
        result.score = round((len(found_pages) / total) * 100)
        result.status = get_status(result.score)

        if missing_pages:
            result.recommendations.append(
                f"Missing transparency pages: {', '.join(missing_pages)}. "
                "These pages build trust signals for both users and search engines."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()