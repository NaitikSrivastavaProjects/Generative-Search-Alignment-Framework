'''
Schema Validation Checker:
Detects whether JSON-LD schema blocks on the page are syntactically valid.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="29 - Schema Validation")
    try:
        script_tags = site_data.soup.find_all("script", type="application/ld+json")

        if not script_tags:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No JSON-LD schema found on page"
            result.recommendations.append("Add structured data (JSON-LD) to the page.")
            return result.to_dict()

        valid_count = 0
        errors = []
        for i, block in enumerate(site_data.json_ld):
            if isinstance(block, dict) and "@context" in block and "@type" in block:
                valid_count += 1
            elif isinstance(block, list):
                valid_count += 1
            else:
                errors.append(f"Block {i+1}: missing '@context' or '@type'")

        # account for blocks that failed to parse entirely (present in HTML but not in json_ld list)
        total_blocks = len(script_tags)
        parsed_blocks = len(site_data.json_ld)
        if parsed_blocks < total_blocks:
            errors.append(f"{total_blocks - parsed_blocks} block(s) failed to parse as valid JSON")

        score = round((valid_count / total_blocks) * 100) if total_blocks else 0

        result.score = score
        result.status = get_status(score)
        result.details["total_blocks"] = total_blocks
        result.details["valid_blocks"] = valid_count
        result.details["errors"] = errors

        if errors:
            result.recommendations.append("Fix schema errors: " + "; ".join(errors))

    except Exception as e:
        result.error = str(e)

    return result.to_dict()