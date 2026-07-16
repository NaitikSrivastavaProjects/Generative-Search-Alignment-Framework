'''
Comparison Table for "vs." Queries Checker:
Detects whether pages with "vs." in the heading contain an HTML table
comparing the two things.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="11 - Comparison Tables for \"vs.\" Queries")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])
        vs_headings = [h for h in headings if " vs" in h.get_text(strip=True).lower()]

        if not vs_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No 'vs.' style headings found on page"
            return result.to_dict()

        tables_found = 0
        checked = []
        for heading in vs_headings:
            heading_text = heading.get_text(strip=True)
            table = heading.find_next("table")
            has_table = table is not None
            if has_table:
                tables_found += 1
            checked.append({"heading": heading_text, "has_table": has_table})

        score = round((tables_found / len(vs_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["checked"] = checked

        if score < 100:
            result.recommendations.append("Add an HTML <table> comparing both items directly under your 'vs.' heading.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()