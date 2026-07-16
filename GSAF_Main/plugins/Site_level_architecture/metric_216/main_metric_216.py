"""
Factor 216

Duplicate Meta Information
"""

from collections import Counter

from models.metric_result import MetricResult
from utils.helpers import extract_text


def run(site_data):
    result = MetricResult(factor="216 - Duplicate Meta Information")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        titles = [
            tag.get("content", "")
            for tag in soup.find_all("meta")
            if tag.get("name", "").lower() in {"title", "description"}
        ]
        title_texts = [text.strip() for text in titles if text.strip()]
        duplicates = [item for item, count in Counter(title_texts).items() if count > 1]

        score = 100 if not duplicates else 40
        result.score = score
        result.status = "Found" if score == 100 else "Partial" if score > 0 else "Not Found"
        result.details["duplicate_meta_found"] = bool(duplicates)
        result.details["duplicate_values"] = duplicates
        result.details["meta_texts_checked"] = len(title_texts)
        result.details["page_text_preview"] = extract_text(soup)[:300]
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
