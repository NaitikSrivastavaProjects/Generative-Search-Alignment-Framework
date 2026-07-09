from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="83 - HTTPS")

    try:
        url = site_data.url
        response = site_data.response

        starts_https = url.startswith("https://")
        ends_https = response.url.startswith("https://")
        http_in_chain = any(r.url.startswith("http://") for r in response.history)

        result.details["original_url"] = url
        result.details["final_url"] = response.url
        result.details["redirect_chain"] = [r.url for r in response.history] + [response.url]

        if starts_https and ends_https and not http_in_chain:
            result.score = 100
        elif not starts_https and ends_https:
            result.score = 60
            result.recommendations.append(
                "HTTP redirects to HTTPS — consider linking directly to the HTTPS version."
            )
        elif http_in_chain:
            result.score = 30
            result.recommendations.append(
                "Redirect chain passes through HTTP before HTTPS — fix to redirect directly to HTTPS."
            )
        else:
            result.score = 0
            result.recommendations.append(
                "Site is not served over HTTPS. This is a ranking penalty and a security risk."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()