from urllib.parse import urlparse

from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):

    url = site_data.url

    score = 0
    details = {}
    recommendations = []

    parsed = urlparse(url)

    path = parsed.path

    details["url"] = url
    details["path"] = path

    # ----------------------------------------
    # HTTPS (20)
    # ----------------------------------------

    if parsed.scheme == "https":
        score += 20
    else:
        recommendations.append(
            "Use HTTPS to improve security and trust."
        )

    # ----------------------------------------
    # URL Length (20)
    # ----------------------------------------

    url_length = len(url)
    details["url_length"] = url_length

    if url_length <= 75:
        score += 20
    elif url_length <= 100:
        score += 15
        recommendations.append(
            "Consider shortening the URL."
        )
    else:
        recommendations.append(
            "URL is too long."
        )

    # ----------------------------------------
    # Query Parameters (15)
    # ----------------------------------------

    if not parsed.query:
        score += 15
    else:
        details["query"] = parsed.query
        recommendations.append(
            "Avoid unnecessary query parameters."
        )

    # ----------------------------------------
    # Fragment (#) (10)
    # ----------------------------------------

    if not parsed.fragment:
        score += 10
    else:
        recommendations.append(
            "Avoid URL fragments (#) for important pages."
        )

    # ----------------------------------------
    # Underscores (10)
    # ----------------------------------------

    if "_" not in path:
        score += 10
    else:
        recommendations.append(
            "Use hyphens (-) instead of underscores (_)."
        )

    # ----------------------------------------
    # URL Depth (10)
    # ----------------------------------------

    depth = len([p for p in path.split("/") if p])

    details["path_depth"] = depth

    if depth <= 3:
        score += 10
    else:
        recommendations.append(
            "Reduce unnecessary folder depth."
        )

    # ----------------------------------------
    # Readable Path (15)
    # ----------------------------------------

    if path not in ["", "/"]:

        readable = (
            "-" in path
            or any(ch.isalpha() for ch in path)
        )

        if readable:
            score += 15
        else:
            recommendations.append(
                "Use descriptive words in the URL."
            )

    else:
        score += 15

    return MetricResult(
        factor="Metric 166 - Stable URL Structure",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()