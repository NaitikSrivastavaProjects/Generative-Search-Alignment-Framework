'''
QAPage Schema Checker:
Detects whether single-question pages use QAPage structured data.
'''
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
    result = MetricResult(factor="18 - QAPage Schema")
    try:
        blocks = site_data.json_ld
        has_qapage = any(_contains_type(b, "QAPage") for b in blocks)

        score = 100 if has_qapage else 0
        result.score = score
        result.status = get_status(score)
        result.details["ld_json_blocks_found"] = len(blocks)

        if not has_qapage:
            result.recommendations.append("Add QAPage schema if this page is structured as a single question with answers.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()