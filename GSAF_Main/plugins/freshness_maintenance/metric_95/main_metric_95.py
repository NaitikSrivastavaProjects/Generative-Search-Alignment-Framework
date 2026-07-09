import requests
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status


WAYBACK_API = "http://archive.org/wayback/available"


def get_snapshot_info(url):
    try:
        response = requests.get(WAYBACK_API, params={"url": url}, timeout=10)
        data = response.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        if snapshot.get("available"):
            return {
                "timestamp": snapshot["timestamp"],
                "status": snapshot.get("status", "200")
            }
        return None
    except Exception:
        return None


def run(site_data):
    result = MetricResult(factor="95 - Deprecation of Outdated Pages")

    try:
        current_status = site_data.response.status_code
        snapshot = get_snapshot_info(site_data.url)

        result.details["current_status_code"] = current_status
        result.details["archive_snapshot_found"] = snapshot is not None

        if not snapshot:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "No archive history found — cannot assess deprecation."
            return result.to_dict()

        result.details["last_snapshot_date"] = snapshot["timestamp"][:8]
        snapshot_date = datetime.strptime(snapshot["timestamp"][:8], "%Y%m%d")
        months_since = (datetime.now() - snapshot_date).days / 30
        result.details["months_since_snapshot"] = round(months_since, 1)

        if current_status in (301, 302, 308):
            result.score = 100
            result.details["note"] = "Page properly redirected — good deprecation practice."
        elif current_status == 404 and snapshot:
            result.score = 80
            result.details["note"] = "Old content removed — good cleanup signal."
        elif current_status == 200 and months_since > 24:
            result.score = 30
            result.recommendations.append(
                f"Page has not been updated in ~{round(months_since)} months. "
                "Consider rewriting, redirecting, or removing this outdated content."
            )
        elif current_status == 200 and months_since <= 24:
            result.score = 70
        else:
            result.score = 50

        result.status = get_status(result.score)
        result.details["informational_note"] = (
            "Full deprecation tracking requires historical scans over time."
        )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()