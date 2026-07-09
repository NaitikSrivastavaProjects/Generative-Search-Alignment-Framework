from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import GLOSSARY_URL_KEYWORDS


def run(site_data):
    result = MetricResult(factor="78 - Glossary Pages")

    try:
        soup = site_data.soup
        url_lower = site_data.url.lower()
        title = soup.find("title")
        title_text = title.get_text().lower() if title else ""

        result.score = 0

        # signal 1: url or title contains glossary keywords
        if any(kw in url_lower or kw in title_text for kw in GLOSSARY_URL_KEYWORDS):
            result.score += 25
            result.details["url_title_signal"] = True
        else:
            result.details["url_title_signal"] = False

        # signal 2: definition list tags
        dl_tags = soup.find_all("dl")
        result.details["definition_list_tags"] = len(dl_tags)
        if dl_tags:
            result.score += 35

        # signal 3: repeated H3 + paragraph pattern (5+ times)
        h3_tags = soup.find_all("h3")
        repeated_pattern_count = 0
        for h3 in h3_tags:
            next_sib = h3.find_next_sibling()
            if next_sib and next_sib.name == "p":
                repeated_pattern_count += 1

        result.details["h3_paragraph_pattern_count"] = repeated_pattern_count
        if repeated_pattern_count >= 5:
            result.score += 25

        # signal 4: DefinedTerm schema
        defined_term_schema = [
            b for b in site_data.json_ld
            if b.get("@type") in ("DefinedTerm", "DefinedTermSet")
        ]
        result.details["defined_term_schema"] = len(defined_term_schema)
        if defined_term_schema:
            result.score += 15

        if result.score == 0:
            result.status = "Not Applicable"
            result.details["note"] = "No glossary page signals detected."
            return result.to_dict()

        result.status = get_status(result.score)

        if not dl_tags:
            result.recommendations.append(
                "Use definition list tags (dl, dt, dd) for glossary content — "
                "these are the semantic HTML for term definitions."
            )
        if not defined_term_schema:
            result.recommendations.append(
                "Add DefinedTerm or DefinedTermSet schema to improve definition box eligibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()