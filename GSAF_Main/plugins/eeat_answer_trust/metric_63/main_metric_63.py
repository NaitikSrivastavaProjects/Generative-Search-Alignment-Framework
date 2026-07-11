from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import AUTHORITATIVE_DOMAINS, MODERATE_DOMAINS


def run(site_data):
    result = MetricResult(factor="63 - Cited Primary Sources")

    try:
        soup = site_data.soup
        all_links = soup.find_all("a", href=True)

        external_links = [a["href"] for a in all_links if a["href"].startswith("http")]

        authoritative_found = [
            link for link in external_links
            if any(d in link for d in AUTHORITATIVE_DOMAINS)
        ]

        moderate_found = [
            link for link in external_links
            if any(d in link for d in MODERATE_DOMAINS)
            and link not in authoritative_found
        ]

        result.details["total_external_links"] = len(external_links)
        result.details["authoritative_links"] = authoritative_found
        result.details["authoritative_count"] = len(authoritative_found)
        result.details["moderate_links"] = moderate_found[:5]
        result.details["moderate_count"] = len(moderate_found)
        result.details["ai_judgment_pending"] = True
        result.details["note"] = (
            "Rule-based citation check complete. "
            "AI quality judgment for borderline sources will be added via ai_batch."
        )

        if len(authoritative_found) >= 3:
            result.score = 80
        elif len(authoritative_found) >= 1:
            result.score = 50
        elif len(moderate_found) >= 2:
            result.score = 30
        elif external_links:
            result.score = 10
        else:
            result.score = 0

        result.status = get_status(result.score)

        if not authoritative_found:
            result.recommendations.append(
                "No authoritative citations found (.gov, .edu, WHO, PubMed etc.). "
                "Link to primary sources to strengthen content credibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()