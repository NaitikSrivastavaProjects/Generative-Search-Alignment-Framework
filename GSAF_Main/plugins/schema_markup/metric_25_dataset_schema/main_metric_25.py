'''
Dataset Schema Checker:
Detects whether pages containing statistics use Dataset schema.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def _contains_type(data, target_type):
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if target_type in types:
            return True
        if "@graph" in data and isinstance(data["@graph"], list):
            return any(_contains_type(item, target_type) for item in data["@graph"])
    elif isinstance(data, list):
        return any(_contains_type(item, target_type) for item in data)
    return False

def run(site_data):
    result = MetricResult(factor="25 - Dataset Schema")
    try:
        blocks = site_data.json_ld
        has_dataset = any(_contains_type(b, "Dataset") for b in blocks)

        text = site_data.soup.get_text()
        stat_matches = re.findall(r"\b\d+([.,]\d+)?%|\b\d{2,}\b", text)
        likely_has_stats = len(stat_matches) >= 3

        if has_dataset:
            score = 100
        elif likely_has_stats:
            score = 20
            result.recommendations.append("Page contains statistics but no Dataset schema — consider adding it.")
        else:
            score = 0

        result.score = score
        result.status = get_status(score)
        result.details["has_dataset_schema"] = has_dataset
        result.details["likely_contains_stats"] = likely_has_stats

    except Exception as e:
        result.error = str(e)

    return result.to_dict()