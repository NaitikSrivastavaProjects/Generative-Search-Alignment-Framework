import whois
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status


def get_domain_age_months(domain):
    try:
        info = whois.whois(domain)
        created = info.creation_date
        if isinstance(created, list):
            created = created[0]
        if not created:
            return None
        months = (datetime.now().year - created.year) * 12 + (datetime.now().month - created.month)
        return max(months, 1)
    except Exception:
        return None


def run(site_data):
    result = MetricResult(factor="184 - Sudden Link Influx")

    if not site_data.opr_data:
        result.error = "Open PageRank API key not configured"
        return result.to_dict()

    try:
        referring_domains = site_data.opr_data.get("referring_domains", 0)
        age_months = get_domain_age_months(site_data.domain)

        if not age_months:
            result.error = "Could not determine domain age via WHOIS"
            return result.to_dict()

        monthly_rate = referring_domains / age_months

        result.details["domain_age_months"] = age_months
        result.details["referring_domains"] = referring_domains
        result.details["monthly_rate"] = round(monthly_rate, 2)

        if monthly_rate > 500:
            result.details["flag"] = "High"
            result.recommendations.append(
                f"Domain is gaining ~{round(monthly_rate)} referring domains/month "
                f"for its age ({age_months} months). Could be legitimate press coverage "
                "or artificial link building — check your backlink history."
            )
        elif monthly_rate > 200:
            result.details["flag"] = "Moderate"
            result.recommendations.append("Link growth rate is elevated. Worth monitoring.")
        else:
            result.details["flag"] = "Normal"

        result.status = "Informational"

    except Exception as e:
        result.error = str(e)

    return result.to_dict()