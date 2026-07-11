from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import AUTHOR_CLASS_PATTERNS


def run(site_data):
    result = MetricResult(factor="57 - Author Entity Profiles")

    try:
        soup = site_data.soup
        result.score = 0

        author_section = soup.find(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in AUTHOR_CLASS_PATTERNS)
        )

        result.details["author_section_found"] = bool(author_section)

        if author_section:
            bio_text = author_section.get_text(strip=True)
            result.details["bio_length_words"] = len(bio_text.split())

            if len(bio_text) > 50:
                result.score += 20

            author_links = author_section.find_all("a", href=True)
            result.details["author_links_count"] = len(author_links)
            if author_links:
                result.score += 20

        person_schema = None
        for block in site_data.json_ld:
            if block.get("@type") == "Person":
                person_schema = block
                break

        result.details["person_schema_found"] = bool(person_schema)

        if person_schema:
            result.score += 20
            valuable_fields = ["name", "jobTitle", "description", "sameAs", "url", "image"]
            found_fields = [f for f in valuable_fields if f in person_schema]
            result.details["schema_fields_found"] = found_fields
            result.details["schema_fields_missing"] = [f for f in valuable_fields if f not in person_schema]
            result.score += min(40, len(found_fields) * 7)

            if result.details["schema_fields_missing"]:
                result.recommendations.append(
                    f"Person schema missing fields: {', '.join(result.details['schema_fields_missing'])}. "
                    "Complete these to strengthen author entity signals."
                )
        else:
            result.recommendations.append(
                "No Person schema found. Add Person schema markup to establish author as a trusted entity."
            )

        if not author_section:
            result.recommendations.append(
                "No author section detected. Add an author bio with links to professional profiles."
            )

        result.score = min(100, result.score)
        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()