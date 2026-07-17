'''
LocalBusiness Schema Checker:
Detects whether local business pages use LocalBusiness schema with
accurate name, address, and phone number.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_localbusiness_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if any("LocalBusiness" in t or t in ("Restaurant", "Store", "ProfessionalService") for t in types):
            found.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_localbusiness_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_localbusiness_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="22 - LocalBusiness Schema")
    try:
        blocks = site_data.json_ld
        lb_blocks = []
        for b in blocks:
            lb_blocks.extend(_find_localbusiness_blocks(b))

        if not lb_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No LocalBusiness schema found"
            result.recommendations.append("Add LocalBusiness schema with name, address, and phone number.")
            return result.to_dict()

        block = lb_blocks[0]
        has_name = bool(block.get("name"))
        has_address = bool(block.get("address"))
        has_phone = bool(block.get("telephone"))

        fields_present = sum([has_name, has_address, has_phone])
        score = round((fields_present / 3) * 100)

        result.score = score
        result.status = get_status(score)
        result.details["has_name"] = has_name
        result.details["has_address"] = has_address
        result.details["has_phone"] = has_phone

        if not has_name:
            result.recommendations.append("Add 'name' field to LocalBusiness schema.")
        if not has_address:
            result.recommendations.append("Add 'address' field to LocalBusiness schema.")
        if not has_phone:
            result.recommendations.append("Add 'telephone' field to LocalBusiness schema.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()