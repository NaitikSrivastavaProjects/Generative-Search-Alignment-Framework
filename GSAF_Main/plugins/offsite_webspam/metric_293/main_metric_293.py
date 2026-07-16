from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="293 - Toxic Backlink Injections")

    if not site_data.opr_data:
        result.error = "Open PageRank API key not configured"
        return result.to_dict()

    try:
        authority = site_data.opr_data.get("open_page_rank", 0)
        referring_domains = site_data.opr_data.get("referring_domains", 0)

        result.details["open_page_rank"] = authority
        result.details["referring_domains"] = referring_domains

        if referring_domains == 0:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "No referring domains found to assess toxicity"
            return result.to_dict()

        # very low authority despite having many referring domains
        # signals those domains are toxic/spammy and not passing value
        if authority >= 7:
            result.score = 100
        elif authority >= 5:
            result.score = 75
        elif authority >= 3:
            result.score = 50
        elif authority >= 1:
            result.score = 25
            result.recommendations.append(
                f"Low authority score ({authority}/10) despite {referring_domains} referring domains. "
                "This may indicate many toxic or spammy backlinks pointing to this site. "
                "Consider auditing your backlink profile."
            )
        else:
            result.score = 0
            result.details["toxic_injection_warning"] = True
            result.recommendations.append(
                f"Very low authority ({authority}/10) with {referring_domains} referring domains. "
                "Strong signal of toxic backlink injections — possibly a negative SEO attack. "
                "Submit a disavow file to Google immediately."
            )

        result.status = get_status(result.score)

        # trigger disavow recommendation if score is critically low
        if result.score < 40:
            result.recommendations.append(
                "Consider submitting a disavow file to tell Google to ignore these harmful links."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()