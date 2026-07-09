import requests
from urllib.parse import urlparse
from models.metric_result import MetricResult
from utils.helpers import get_status


IMPORTANT_CRAWLERS = [
    "Googlebot", "Google-Extended", "GPTBot",
    "ClaudeBot", "PerplexityBot", "Bingbot"
]


def is_path_blocked(rules, path):
    for rule in rules:
        if rule == "/" or path.startswith(rule):
            return True
    return False


def parse_robots(content, url_path):
    blocked_crawlers = []
    current_agents = []
    disallow_rules = {}

    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agents = [agent]
            for a in current_agents:
                if a not in disallow_rules:
                    disallow_rules[a] = []
        elif line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            for agent in current_agents:
                disallow_rules.setdefault(agent, []).append(path)

    # check wildcard rules first
    wildcard_rules = disallow_rules.get("*", [])

    for crawler in IMPORTANT_CRAWLERS:
        crawler_rules = disallow_rules.get(crawler, [])
        all_rules = crawler_rules + wildcard_rules

        if is_path_blocked(all_rules, url_path):
            blocked_crawlers.append(crawler)

    return blocked_crawlers


def run(site_data):
    result = MetricResult(factor="88 - Robots.txt Not Blocking Snippet Bots")

    try:
        domain = site_data.domain
        url = site_data.url
        url_path = urlparse(url).path or "/"

        robots_url = f"https://{domain}/robots.txt"
        response = requests.get(robots_url, timeout=8)

        if response.status_code != 200:
            result.score = 70
            result.status = get_status(result.score)
            result.details["robots_txt_found"] = False
            result.details["note"] = "No robots.txt found — defaults to allowing all crawlers."
            return result.to_dict()

        result.details["robots_txt_found"] = True
        blocked = parse_robots(response.text, url_path)
        result.details["blocked_crawlers"] = blocked

        if not blocked:
            result.score = 100
        elif "Googlebot" in blocked:
            result.score = 0
            result.details["critical"] = True
            result.recommendations.append(
                "CRITICAL: Googlebot is blocked in robots.txt — this page cannot be indexed or ranked."
            )
        else:
            result.score = 40
            result.recommendations.append(
                f"These crawlers are blocked: {', '.join(blocked)}. "
                "This may reduce visibility in AI answer engines and other search platforms."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()