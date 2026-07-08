import requests
from urllib.parse import urljoin

from models.metric_result import MetricResult
from utils.helpers import get_status


KEYWORDS = [
    "ai",
    "llm",
    "gpt",
    "claude",
    "gemini",
    "perplexity",
    "crawl",
    "training",
    "usage",
    "license"
]


def run(site_data):

    score = 0
    details = {}
    recommendations = []

    llms_url = urljoin(site_data.url, "/llms.txt")

    details["llms_url"] = llms_url

    try:

        response = requests.get(
            llms_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

    except Exception:

        return MetricResult(
            factor="Metric 63 - LLMs.txt Availability",
            score=0,
            status="Poor",
            details=details,
            recommendations=[
                "Unable to access llms.txt."
            ]
        ).to_dict()

    details["status_code"] = response.status_code

    # ----------------------------------------
    # HTTP 200 (25)
    # ----------------------------------------

    if response.status_code == 200:

        score += 25

    else:

        recommendations.append(
            "Create an llms.txt file in the website root."
        )

        return MetricResult(
            factor="Metric 63 - LLMs.txt Availability",
            score=score,
            status=get_status(score),
            details=details,
            recommendations=recommendations
        ).to_dict()

    content = response.text.strip()

    # ----------------------------------------
    # File Not Empty (15)
    # ----------------------------------------

    if content:

        score += 15

    else:

        recommendations.append(
            "llms.txt is empty."
        )

    # ----------------------------------------
    # Content Length (20)
    # ----------------------------------------

    length = len(content)

    details["content_length"] = length

    if length >= 200:

        score += 20

    elif length >= 100:

        score += 10

        recommendations.append(
            "Expand llms.txt with additional AI guidance."
        )

    else:

        recommendations.append(
            "llms.txt should contain more detailed instructions."
        )

    # ----------------------------------------
    # AI Guidance Keywords (30)
    # ----------------------------------------

    found = []

    lower_content = content.lower()

    for keyword in KEYWORDS:

        if keyword in lower_content:

            found.append(keyword)

    details["keywords_found"] = found

    if len(found) >= 6:

        score += 30

    elif len(found) >= 3:

        score += 20

    elif len(found) >= 1:

        score += 10

    else:

        recommendations.append(
            "Include AI usage, crawl and licensing guidance."
        )

    # ----------------------------------------
    # Allow / Disallow Instructions (10)
    # ----------------------------------------

    if (
        "allow" in lower_content
        or "disallow" in lower_content
        or "permit" in lower_content
        or "prohibit" in lower_content
    ):

        score += 10

    else:

        recommendations.append(
            "Specify whether AI systems are allowed or restricted."
        )

    return MetricResult(
        factor="Metric 63 - LLMs.txt Availability",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()