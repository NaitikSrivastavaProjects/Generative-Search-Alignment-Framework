from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import DISCLOSURE_KEYWORDS, COMMERCIAL_INTENT_SIGNALS


def run(site_data):
    result = MetricResult(factor="69 - Conflict-of-Interest Disclosure")

    try:
        soup = site_data.soup
        text = soup.get_text().lower()
        title = soup.find("title")
        title_text = title.get_text().lower() if title else ""
        url_lower = site_data.url.lower()

        disclosures_found = [kw for kw in DISCLOSURE_KEYWORDS if kw in text]
        commercial_signals = [
            kw for kw in COMMERCIAL_INTENT_SIGNALS
            if kw in text or kw in title_text or kw in url_lower
        ]

        result.details["disclosures_found"] = disclosures_found
        result.details["commercial_signals_found"] = commercial_signals

        if disclosures_found:
            result.score = 100
            result.details["reasoning"] = "Disclosure present — transparent commercial relationship."
        elif commercial_signals and not disclosures_found:
            result.score = 20
            result.details["reasoning"] = "Commercial content detected without disclosure."
            result.recommendations.append(
                f"Commercial signals detected ({', '.join(commercial_signals)}) but no disclosure found. "
                "Add an affiliate or advertiser disclosure to maintain trust and comply with guidelines."
            )
        else:
            result.score = 70
            result.details["reasoning"] = "No commercial signals detected — disclosure likely not required."

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()