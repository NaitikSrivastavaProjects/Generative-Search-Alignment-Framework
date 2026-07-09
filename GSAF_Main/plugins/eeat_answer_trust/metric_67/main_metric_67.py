import re
from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import DATE_KEYWORDS


def run(site_data):
    result = MetricResult(factor="67 - Last Updated Date Visible")

    try:
        soup = site_data.soup
        page_text = soup.get_text().lower()

        visible_date_found = False
        for keyword in DATE_KEYWORDS:
            if keyword in page_text:
                idx = page_text.find(keyword)
                surrounding = page_text[idx:idx+60]
                if re.search(
                    r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4}',
                    surrounding
                ):
                    visible_date_found = True
                    break

        date_published = None
        date_modified = None
        for block in site_data.json_ld:
            if "datePublished" in block:
                date_published = block["datePublished"]
            if "dateModified" in block:
                date_modified = block["dateModified"]

        result.details["visible_date_found"] = visible_date_found
        result.details["schema_date_published"] = date_published
        result.details["schema_date_modified"] = date_modified

        result.score = 0
        if visible_date_found:
            result.score += 40
        if date_published:
            result.score += 30
        if date_modified:
            result.score += 30

        result.status = get_status(result.score)

        if not visible_date_found:
            result.recommendations.append("Add a visible publish or update date near the top of the page.")
        if not date_published:
            result.recommendations.append("Add datePublished to your JSON-LD schema markup.")
        if not date_modified:
            result.recommendations.append("Add dateModified to your JSON-LD schema markup.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()