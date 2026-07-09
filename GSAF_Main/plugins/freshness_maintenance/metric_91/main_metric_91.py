import requests
from datetime import datetime
from models.metric_result import MetricResult
from utils.helpers import get_status


WAYBACK_API = "http://archive.org/wayback/available"


def get_last_snapshot(url):
    try:
        response = requests.get(WAYBACK_API, params={"url": url}, timeout=10)
        data = response.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        if snapshot.get("available"):
            return snapshot.get("timestamp")
        return None
    except Exception:
        return None


def run(site_data):
    result = MetricResult(factor="91 - Regular Answer Audits")

    try:
        snapshot_timestamp = get_last_snapshot(site_data.url)
        result.details["last_wayback_snapshot"] = snapshot_timestamp

        if not snapshot_timestamp:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "No archive history found — cannot assess update frequency."
            return result.to_dict()

        snapshot_date = datetime.strptime(snapshot_timestamp[:8], "%Y%m%d")
        months_since_update = (datetime.now() - snapshot_date).days / 30

        result.details["months_since_last_update"] = round(months_since_update, 1)

        if months_since_update <= 3:
            result.score = 100
        elif months_since_update <= 6:
            result.score = 70
        elif months_since_update <= 12:
            result.score = 40
        else:
            result.score = 20
            result.recommendations.append(
                f"Page has not been updated in ~{round(months_since_update)} months. "
                "Regularly audit and refresh answer content to maintain ranking positions."
            )

        result.status = get_status(result.score)
        result.details["note"] = (
            "For full audit tracking run regular scans and compare scores over time."
        )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()