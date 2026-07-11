import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import AUTHOR_CLASS_PATTERNS


AUTHOR_URL_PATTERNS = ["/author/", "/writers/", "/team/", "/contributors/", "/about/"]
PERSON_SCHEMA_FIELDS = ["name", "jobTitle", "description", "sameAs", "url", "image"]


def run(site_data):
    result = MetricResult(factor="62 - Author Page with Schema")

    try:
        soup = site_data.soup
        base_url = site_data.url

        author_link = None
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(pattern in href for pattern in AUTHOR_URL_PATTERNS):
                author_link = urljoin(base_url, a["href"])
                break

        if not author_link:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "No author profile page link found. "
                "Create a dedicated author page at /author/ or /team/ with Person schema."
            )
            return result.to_dict()

        result.details["author_page_url"] = author_link

        try:
            author_response = requests.get(
                author_link,
                headers={"User-Agent": "Mozilla/5.0 SEO Analyzer Bot"},
                timeout=10
            )
            author_soup = BeautifulSoup(author_response.text, "html.parser")
        except Exception:
            result.score = 20
            result.status = get_status(result.score)
            result.recommendations.append("Author page link found but page could not be fetched.")
            return result.to_dict()

        person_schema = None
        for script in author_soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Person":
                    person_schema = data
                    break
            except Exception:
                continue

        result.details["person_schema_found"] = bool(person_schema)
        result.score = 40  # base score for author page existing

        if not person_schema:
            result.recommendations.append(
                "Author page exists but no Person schema found. "
                "Add Person schema with name, jobTitle, and sameAs links."
            )
        else:
            found_fields = [f for f in PERSON_SCHEMA_FIELDS if f in person_schema]
            missing_fields = [f for f in PERSON_SCHEMA_FIELDS if f not in person_schema]

            result.details["schema_fields_found"] = found_fields
            result.details["schema_fields_missing"] = missing_fields

            schema_score = round((len(found_fields) / len(PERSON_SCHEMA_FIELDS)) * 60)
            result.score = 40 + schema_score

            if missing_fields:
                result.recommendations.append(
                    f"Person schema missing: {', '.join(missing_fields)}. "
                    "Complete these fields to strengthen author entity signals."
                )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()