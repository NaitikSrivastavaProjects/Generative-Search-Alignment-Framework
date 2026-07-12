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
        result.details["moderate_count"] = len(moderate_found)

        if len(authoritative_found) >= 3:
            base_score = 80
        elif len(authoritative_found) >= 1:
            base_score = 50
        elif len(moderate_found) >= 2:
            base_score = 30
        elif external_links:
            base_score = 10
        else:
            base_score = 0

        ai_data = site_data.ai_results.get("metric_63", {})
        if ai_data:
            quality = ai_data.get("citation_quality", "").lower()
            result.details["ai_citation_quality"] = quality
            result.details["ai_reasoning"] = ai_data.get("reasoning", "")
            quality_bonus = {"high": 20, "medium": 10, "low": 0}.get(quality, 0)
            result.score = min(100, base_score + quality_bonus)
        else:
            result.score = base_score

        result.status = get_status(result.score)

        if not authoritative_found:
            result.recommendations.append(
                "No authoritative citations found (.gov, .edu, WHO, PubMed etc.). "
                "Link to primary sources to strengthen content credibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()