from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import BRAND_SCHEMA_FIELDS


BRAND_SCHEMA_TYPES = ["Organization", "LocalBusiness", "Corporation", "Company"]


def run(site_data):
    result = MetricResult(factor="58 - Brand Schema Fields")

    try:
        brand_schema = None
        for block in site_data.json_ld:
            if block.get("@type") in BRAND_SCHEMA_TYPES:
                brand_schema = block
                break

        if not brand_schema:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "No Organization schema found. Add Organization schema markup "
                "with founder, foundingDate, and address to strengthen brand entity signals."
            )
            return result.to_dict()

        result.details["schema_type_found"] = brand_schema.get("@type")
        found_fields = {}
        missing_fields = []

        for field, weight in BRAND_SCHEMA_FIELDS.items():
            if field in brand_schema:
                found_fields[field] = brand_schema[field]
                result.score = (result.score or 0) + weight
            else:
                missing_fields.append(field)

        result.details["fields_found"] = found_fields
        result.details["fields_missing"] = missing_fields
        result.score = min(100, result.score)
        result.status = get_status(result.score)

        if missing_fields:
            result.recommendations.append(
                f"Brand schema missing: {', '.join(missing_fields)}. "
                "Complete these fields to improve Knowledge Panel eligibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()