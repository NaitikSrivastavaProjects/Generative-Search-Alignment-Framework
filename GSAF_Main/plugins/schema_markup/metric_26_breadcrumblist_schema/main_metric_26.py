'''
BreadcrumbList Schema Checker:
Detects whether pages include BreadcrumbList schema.
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
    result = MetricResult(factor="26 - BreadcrumbList Schema")
    try:
        blocks = site_data.json_ld
        has_breadcrumb = any(_contains_type(b, "BreadcrumbList") for b in blocks)

        score = 100 if has_breadcrumb else 0
        result.score = score
        result.status = get_status(score)
        result.details["ld_json_blocks_found"] = len(blocks)

        if not has_breadcrumb:
            result.recommendations.append("Add BreadcrumbList schema to show the page's position in your site hierarchy.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()