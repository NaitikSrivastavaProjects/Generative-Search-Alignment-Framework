from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="186 - Low-Quality Directory Backlinks")

    if not site_data.opr_data:
        result.error = "Open PageRank API key not configured"
        return result.to_dict()

    try:
        authority = site_data.opr_data.get("open_page_rank", 0)
        referring_domains = site_data.opr_data.get("referring_domains", 0)

        result.details["open_page_rank"] = authority
        result.details["referring_domains"] = referring_domains

        # low authority + high referring domain count = likely directory spam
        # a clean site has authority proportional to its referring domains
        if referring_domains == 0:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "No referring domains found"
            return result.to_dict()

        # authority per 1000 referring domains as a quality ratio
        quality_ratio = authority / (referring_domains / 1000)
        result.details["quality_ratio"] = round(quality_ratio, 2)

        if quality_ratio >= 5:
            result.score = 100
        elif quality_ratio >= 2:
            result.score = 70
        elif quality_ratio >= 1:
            result.score = 40
        elif quality_ratio >= 0.5:
            result.score = 10
        else:
            result.score = 0

        result.status = get_status(result.score)

        if result.score < 40:
            result.recommendations.append(
                f"Low authority ({authority}/10) relative to referring domain count ({referring_domains}). "
                "This pattern suggests many low-quality directory backlinks. "
                "Audit your backlink profile and disavow spammy links."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()