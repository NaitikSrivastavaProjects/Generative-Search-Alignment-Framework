'''
Event Schema Checker:
Detects whether event pages use Event schema with date/time information.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_event_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if any("Event" in t for t in types):
            found.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_event_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_event_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="23 - Event Schema")
    try:
        blocks = site_data.json_ld
        event_blocks = []
        for b in blocks:
            event_blocks.extend(_find_event_blocks(b))

        if not event_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No Event schema found"
            result.recommendations.append("Add Event schema if this page is about an event.")
            return result.to_dict()

        block = event_blocks[0]
        has_start_date = bool(block.get("startDate"))
        has_location = bool(block.get("location"))

        if has_start_date and has_location:
            score = 100
        elif has_start_date or has_location:
            score = 60
            if not has_start_date:
                result.recommendations.append("Add 'startDate' to Event schema.")
            if not has_location:
                result.recommendations.append("Add 'location' to Event schema.")
        else:
            score = 30
            result.recommendations.append("Add 'startDate' and 'location' fields to Event schema.")

        result.score = score
        result.status = get_status(score)
        result.details["has_start_date"] = has_start_date
        result.details["has_location"] = has_location

    except Exception as e:
        result.error = str(e)

    return result.to_dict()