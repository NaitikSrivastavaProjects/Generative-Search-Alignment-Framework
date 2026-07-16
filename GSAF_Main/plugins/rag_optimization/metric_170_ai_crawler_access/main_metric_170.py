from models.metric_result import MetricResult
from utils.helpers import get_status


AI_CRAWLERS = [
    "GPTBot",
    "Google-Extended",
    "ClaudeBot",
    "CCBot",
    "Amazonbot",
    "Bytespider",
    "PerplexityBot",
    "Applebot-Extended"
]


def run(site_data):

    robots_txt = getattr(site_data, 'robots_txt', "")

    score = 0
    details = {}
    recommendations = []

    robots_lower = robots_txt.lower()

    allowed = []
    blocked = []
    not_found = []

    # ----------------------------------------
    # 1. AI Crawler Rules (80)
    # ----------------------------------------

    for crawler in AI_CRAWLERS:

        crawler_lower = crawler.lower()

        if f"user-agent: {crawler_lower}" in robots_lower:

            lines = robots_lower.splitlines()
            current_agent = None

            disallow_all = False

            for line in lines:

                line = line.strip().lower()

                if line.startswith("user-agent:"):
                    current_agent = line.replace(
                        "user-agent:",
                        ""
                    ).strip()

                elif current_agent == crawler_lower:

                    if line.startswith("disallow:"):

                        value = line.replace(
                            "disallow:",
                            ""
                        ).strip()

                        if value == "/":
                            disallow_all = True

            if disallow_all:
                blocked.append(crawler)

            else:
                allowed.append(crawler)

        else:
            not_found.append(crawler)

    details["allowed_ai_crawlers"] = allowed
    details["blocked_ai_crawlers"] = blocked
    details["no_specific_rule"] = not_found

    if len(allowed) > 0:
        score += 80

    elif len(blocked) > 0:
        score += 20

        recommendations.append(
            "AI crawlers are explicitly blocked. Allow trusted AI crawlers if desired."
        )

    else:
        recommendations.append(
            "No AI crawler directives found in robots.txt."
        )

    # ----------------------------------------
    # 2. robots.txt Exists (20)
    # ----------------------------------------

    if robots_txt.strip():
        score += 20
        details["robots_txt_found"] = True

    else:
        details["robots_txt_found"] = False

        recommendations.append(
            "Create a robots.txt file with AI crawler directives."
        )

    # ----------------------------------------
    # Final Result
    # ----------------------------------------

    final_score = min(score, 100)

    return MetricResult(
        factor="Metric 170 - AI Crawler Access",
        score=final_score,
        status=get_status(final_score),
        details=details,
        recommendations=recommendations
    ).to_dict()