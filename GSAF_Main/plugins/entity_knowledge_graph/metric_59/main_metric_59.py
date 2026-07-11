import requests
from models.metric_result import MetricResult
from utils.helpers import get_status


WIKIPEDIA_SEARCH = "https://en.wikipedia.org/w/api.php"


def run(site_data):
    result = MetricResult(factor="59 - Consistent Entity Mentions Across Web")

    try:
        soup = site_data.soup
        title_tag = soup.find("title")
        entity_name = title_tag.get_text(strip=True).split("|")[0].split("-")[0].strip() if title_tag else site_data.domain

        result.details["entity_searched"] = entity_name

        response = requests.get(
            WIKIPEDIA_SEARCH,
            params={
                "action": "query",
                "list": "search",
                "srsearch": entity_name,
                "format": "json",
                "srlimit": 10
            },
            timeout=10
        )
        data = response.json()
        search_results = data["query"]["search"]
        result_count = len(search_results)
        total_hits = data["query"].get("searchinfo", {}).get("totalhits", 0)

        result.details["wikipedia_results_found"] = result_count
        result.details["total_wikipedia_hits"] = total_hits

        if total_hits >= 6:
            result.score = 100
        elif total_hits >= 3:
            result.score = 70
        elif total_hits >= 1:
            result.score = 40
        else:
            result.score = 0
            result.recommendations.append(
                f"No cross-web mentions found for '{entity_name}' on Wikipedia. "
                "Build consistent entity presence across authoritative platforms."
            )

        result.status = get_status(result.score)
        result.details["limitation"] = (
            "Full cross-web mention tracking requires paid APIs. "
            "This score uses Wikipedia search result count as a proxy."
        )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()