'''
Product + Review Schema Checker:
Detects whether product pages include Product and Review schema.
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
    result = MetricResult(factor="21 - Product + Review Schema")
    try:
        blocks = site_data.json_ld
        has_product = any(_contains_type(b, "Product") for b in blocks)
        has_review = any(_contains_type(b, "Review") or _contains_type(b, "AggregateRating") for b in blocks)

        if has_product and has_review:
            score = 100
        elif has_product:
            score = 60
            result.recommendations.append("Add Review/AggregateRating schema alongside your existing Product schema.")
        elif has_review:
            score = 40
            result.recommendations.append("Add Product schema alongside your existing Review schema.")
        else:
            score = 0
            result.recommendations.append("Add both Product and Review schema if this is a product page.")

        result.score = score
        result.status = get_status(score)
        result.details["has_product_schema"] = has_product
        result.details["has_review_schema"] = has_review

    except Exception as e:
        result.error = str(e)

    return result.to_dict()