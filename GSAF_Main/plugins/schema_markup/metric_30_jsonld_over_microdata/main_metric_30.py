'''
JSON-LD Over Microdata Checker:
Detects whether structured data is implemented using JSON-LD format
rather than Microdata.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="30 - JSON-LD Over Microdata")
    try:
        soup = site_data.soup
        jsonld_blocks = soup.find_all("script", type="application/ld+json")
        microdata_elements = soup.find_all(attrs={"itemscope": True})

        has_jsonld = len(jsonld_blocks) > 0
        has_microdata = len(microdata_elements) > 0

        if has_jsonld and not has_microdata:
            score = 100
        elif has_jsonld and has_microdata:
            score = 70
            result.recommendations.append("Both JSON-LD and Microdata detected — consolidate to JSON-LD only to avoid conflicting signals.")
        elif has_microdata and not has_jsonld:
            score = 20
            result.recommendations.append("Migrate from Microdata to JSON-LD format, which is cleaner and Google's recommended approach.")
        else:
            score = 0
            result.recommendations.append("No structured data found — add schema markup using JSON-LD format.")

        result.score = score
        result.status = get_status(score)
        result.details["jsonld_blocks_found"] = len(jsonld_blocks)
        result.details["microdata_elements_found"] = len(microdata_elements)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()