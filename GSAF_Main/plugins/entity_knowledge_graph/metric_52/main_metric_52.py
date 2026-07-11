import requests
from models.metric_result import MetricResult
from utils.helpers import get_status


WIKIPEDIA_SEARCH = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary"


def search_wikipedia(entity_name):
    try:
        response = requests.get(
            WIKIPEDIA_SEARCH,
            params={
                "action": "query",
                "list": "search",
                "srsearch": entity_name,
                "format": "json",
                "srlimit": 3
            },
            timeout=10
        )
        return response.json()["query"]["search"]
    except Exception:
        return []


def get_page_summary(title):
    try:
        response = requests.get(
            f"{WIKIPEDIA_SUMMARY}/{title.replace(' ', '_')}",
            timeout=10
        )
        return response.json()
    except Exception:
        return {}


def run(site_data):
    result = MetricResult(factor="52 - Wikipedia/Wikidata Presence")

    try:
        soup = site_data.soup
        title_tag = soup.find("title")
        entity_name = title_tag.get_text(strip=True).split("|")[0].split("-")[0].strip() if title_tag else site_data.domain

        result.details["entity_searched"] = entity_name
        search_results = search_wikipedia(entity_name)

        if not search_results:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                f"No Wikipedia page found for '{entity_name}'. "
                "A Wikipedia presence is the strongest single entity legitimacy signal."
            )
            return result.to_dict()

        top_result = search_results[0]
        top_title = top_result["title"].lower()
        entity_lower = entity_name.lower()

        is_match = entity_lower in top_title or top_title in entity_lower

        if not is_match:
            result.score = 10
            result.details["wikipedia_title"] = top_result["title"]
            result.details["match"] = False
            result.recommendations.append(
                "Wikipedia results found but no clear match for this entity. "
                "The page may not have strong enough entity signals."
            )
            return result.to_dict()

        summary = get_page_summary(top_result["title"])
        result.details["wikipedia_title"] = top_result["title"]
        result.details["wikipedia_description"] = summary.get("description", "")
        result.details["wikipedia_summary"] = summary.get("extract", "")[:200]
        result.details["match"] = True
        result.score = 100
        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()