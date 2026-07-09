import re
import requests
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status


WAYBACK_API = "http://archive.org/wayback/available"


def get_last_snapshot_date(url):
    try:
        response = requests.get(WAYBACK_API, params={"url": url}, timeout=10)
        data = response.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        if snapshot.get("available"):
            return datetime.strptime(snapshot["timestamp"][:8], "%Y%m%d")
        return None
    except Exception:
        return None


def run(site_data):
    result = MetricResult(factor="93 - Statistic Refresh Cadence")

    try:
        soup = site_data.soup
        text = soup.get_text()
        current_year = datetime.now().year

        stat_pattern = re.compile(r'(\b20\d{2}\b)(?=.*?(?:%|percent|respondents|participants|users|people))', re.IGNORECASE)
        year_matches = stat_pattern.findall(text)

        general_years = re.findall(r'\b(20\d{2})\b', text)
        all_years = [int(y) for y in (year_matches if year_matches else general_years)]

        result.details["years_found"] = list(set(all_years))

        if all_years:
            avg_year = sum(all_years) / len(all_years)
            age_gap = current_year - avg_year
            result.details["average_statistic_year"] = round(avg_year, 1)
            result.details["years_behind_current"] = round(age_gap, 1)

            if age_gap <= 1:
                result.score = 100
            elif age_gap <= 2:
                result.score = 70
            elif age_gap <= 3:
                result.score = 50
            elif age_gap <= 5:
                result.score = 30
            else:
                result.score = 10
                result.recommendations.append(
                    f"Statistics average {round(age_gap, 1)} years old. "
                    "Update data points and statistics to improve freshness signals."
                )
        else:
            result.score = 50
            result.details["note"] = "No year references found near statistics."

        snapshot_date = get_last_snapshot_date(site_data.url)
        if snapshot_date:
            months_since = (datetime.now() - snapshot_date).days / 30
            result.details["wayback_last_update_months_ago"] = round(months_since, 1)
            if months_since <= 3:
                result.score = min(100, result.score + 15)

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()