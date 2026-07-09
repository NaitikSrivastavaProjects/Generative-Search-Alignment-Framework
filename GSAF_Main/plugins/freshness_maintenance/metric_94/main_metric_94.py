import re
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import YEAR_SENSITIVE_KEYWORDS


def run(site_data):
    result = MetricResult(factor="94 - Year-in-Title Updates")

    try:
        soup = site_data.soup
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        current_year = datetime.now().year

        result.details["title"] = title
        result.details["current_year"] = current_year

        combined = (title + site_data.url).lower()
        is_year_sensitive = any(kw in combined for kw in YEAR_SENSITIVE_KEYWORDS)
        result.details["year_sensitive"] = is_year_sensitive

        if not is_year_sensitive:
            result.status = "Not Applicable"
            result.details["message"] = "Evergreen content — year update not required."
            return result.to_dict()

        years_in_title = re.findall(r'\b(20\d{2})\b', title)

        if not years_in_title:
            result.score = 60
            result.status = get_status(result.score)
            result.recommendations.append(
                f"Consider adding {current_year} to your title for freshness signals."
            )
            return result.to_dict()

        found_year = int(years_in_title[0])
        years_behind = current_year - found_year
        result.details["year_found"] = found_year
        result.details["years_behind"] = years_behind

        score_map = {0: 100, 1: 60, 2: 30}
        result.score = score_map.get(years_behind, 0)
        result.status = get_status(result.score)

        if years_behind > 0:
            result.recommendations.append(
                f"Title contains {found_year} but current year is {current_year}. "
                "Update the year and review content for stale information."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()