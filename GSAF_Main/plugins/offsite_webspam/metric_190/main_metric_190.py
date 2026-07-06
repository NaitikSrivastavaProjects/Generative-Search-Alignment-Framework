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
    result = MetricResult(factor="190 - Google Sandbox")

    try:
        age_months = get_domain_age_months(site_data.domain)

        if not age_months:
            result.error = "Could not determine domain age via WHOIS"
            return result.to_dict()

        result.details["domain_age_months"] = age_months
        result.details["domain_age_years"] = round(age_months / 12, 1)

        if age_months > 24:
            result.score = 100
            result.details["sandbox_risk"] = "None"
        elif age_months > 12:
            result.score = 85
            result.details["sandbox_risk"] = "None"
        elif age_months > 6:
            result.score = 65
            result.details["sandbox_risk"] = "Low"
        elif age_months > 3:
            result.score = 35
            result.details["sandbox_risk"] = "Moderate"
            result.recommendations.append(
                f"Domain is only {age_months} months old. New domains often experience "
                "a probationary period where rankings are temporarily suppressed. "
                "Focus on building quality content and natural backlinks."
            )
        else:
            result.score = 10
            result.details["sandbox_risk"] = "High"
            result.recommendations.append(
                f"Domain is only {age_months} months old. It is very likely in a "
                "sandbox period. Continue publishing quality content consistently — "
                "this typically resolves within 6 months."
            )

        result.status = get_status(result.score)
        result.details["note"] = "Google Sandbox is an observed phenomenon, not officially confirmed by Google."

    except Exception as e:
        result.error = str(e)

    return result.to_dict()