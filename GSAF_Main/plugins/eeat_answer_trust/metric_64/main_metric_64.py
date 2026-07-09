import re
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="64 - Recency of Citations")

    try:
        soup = site_data.soup
        current_year = datetime.now().year

        page_text = soup.get_text()
        text_years = re.findall(r'\b(20\d{2})\b', page_text)

        link_years = []
        for a in soup.find_all("a", href=True):
            link_years.extend(re.findall(r'\b(20\d{2})\b', a["href"]))

        all_years = [int(y) for y in text_years + link_years]

        if not all_years:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "No year references found — cannot assess citation recency."
            return result.to_dict()

        avg_year = sum(all_years) / len(all_years)
        most_recent = max(all_years)
        oldest = min(all_years)
        age_gap = current_year - avg_year

        result.details["average_citation_year"] = round(avg_year, 1)
        result.details["most_recent_year"] = most_recent
        result.details["oldest_year"] = oldest
        result.details["years_behind_current"] = round(age_gap, 1)

        if age_gap <= 1:
            result.score = 100
        elif age_gap <= 2:
            result.score = 80
        elif age_gap <= 3:
            result.score = 60
        elif age_gap <= 5:
            result.score = 40
        else:
            result.score = 20
            result.recommendations.append(
                f"Citations average {round(age_gap, 1)} years old. "
                "Update references to more recent sources to improve freshness signals."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()