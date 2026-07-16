import requests
from urllib.parse import urljoin

from models.metric_result import MetricResult
from utils.helpers import get_status


AI_BOTS = [
    "GPTBot",
    "Google-Extended",
    "ClaudeBot",
    "PerplexityBot"
]


def run(site_data):

    score = 0
    details = {}
    recommendations = []

    robots_url = urljoin(site_data.url, "/robots.txt")

    try:

        response = requests.get(
            robots_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

    except Exception:

        return MetricResult(
            factor="Metric 62 - Robots.txt Accessibility",
            score=0,
            status="Poor",
            details={
                "robots_url": robots_url
            },
            recommendations=[
                "robots.txt could not be accessed."
            ]
        ).to_dict()

    details["robots_url"] = robots_url
    details["status_code"] = response.status_code

    # ----------------------------------------
    # Robots.txt Exists (20)
    # ----------------------------------------

    if response.status_code == 200:

        score += 20

    else:

        recommendations.append(
            "Create a valid robots.txt file."
        )

        return MetricResult(
            factor="Metric 62 - Robots.txt Accessibility",
            score=score,
            status=get_status(score),
            details=details,
            recommendations=recommendations
        ).to_dict()

    content = response.text

    # ----------------------------------------
    # Not Empty (10)
    # ----------------------------------------

    if content.strip():

        score += 10

    else:

        recommendations.append(
            "robots.txt is empty."
        )

    # ----------------------------------------
    # Global Crawl Block (25)
    # ----------------------------------------

    if "Disallow: /" not in content:

        score += 25

    else:

        recommendations.append(
            "Website blocks crawlers using 'Disallow: /'."
        )

    # ----------------------------------------
    # Sitemap Mentioned (20)
    # ----------------------------------------

    if "Sitemap:" in content:

        score += 20
        details["sitemap_present"] = True

    else:

        details["sitemap_present"] = False

        recommendations.append(
            "Add Sitemap location inside robots.txt."
        )

    # ----------------------------------------
    # AI Bot Directives (25)
    # ----------------------------------------

    detected = []

    for bot in AI_BOTS:

        if bot.lower() in content.lower():

            detected.append(bot)

    details["ai_bot_directives"] = detected

    if len(detected) == len(AI_BOTS):

        score += 25

    elif len(detected) >= 2:

        score += 15

    elif len(detected) >= 1:

        score += 8

    else:

        recommendations.append(
            "Consider adding directives for GPTBot, Google-Extended, ClaudeBot and PerplexityBot."
        )

    return MetricResult(
        factor="Metric 162 - Robots.txt Accessibility",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()