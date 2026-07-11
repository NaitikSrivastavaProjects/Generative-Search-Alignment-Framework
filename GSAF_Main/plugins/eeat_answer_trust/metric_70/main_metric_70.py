from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import REGISTRY_DOMAINS


def run(site_data):
    result = MetricResult(factor="70 - Real-World Verification")

    try:
        soup = site_data.soup
        all_links = [a["href"] for a in soup.find_all("a", href=True)]

        found_registries = []
        for link in all_links:
            for domain in REGISTRY_DOMAINS:
                if domain in link:
                    found_registries.append({"domain": domain, "url": link})
                    break

        result.details["registries_found"] = found_registries
        result.details["registry_count"] = len(found_registries)
        result.details["limitation"] = (
            "Link presence confirmed but profile matching requires manual verification — "
            "cannot auto-confirm the linked profile belongs to this author/organization."
        )

        result.score = min(100, len(found_registries) * 35)
        result.status = get_status(result.score)

        if not found_registries:
            result.recommendations.append(
                "No professional registry links found (ORCID, LinkedIn, AMA, Bar Association etc.). "
                "Link to external professional profiles to verify real-world credentials."
            )
        else:
            result.recommendations.append(
                "Registry links found — manually verify these profiles belong to the stated author/organization."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()