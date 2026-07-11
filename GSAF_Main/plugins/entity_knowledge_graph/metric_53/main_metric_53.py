from models.metric_result import MetricResult
from utils.helpers import get_status
from plugins.entity_knowledge_graph.metric_52.main_metric_52 import run as run_52
from plugins.entity_knowledge_graph.metric_58.main_metric_58 import run as run_58


def run(site_data):
    result = MetricResult(factor="53 - Knowledge Panel Eligibility")

    try:
        wikipedia_result = run_52(site_data)
        brand_schema_result = run_58(site_data)

        wiki_score = wikipedia_result.get("score") or 0
        schema_score = brand_schema_result.get("score") or 0

        derived_score = round((wiki_score + schema_score) / 2)

        result.score = derived_score
        result.status = get_status(result.score)
        result.details["wikipedia_score"] = wiki_score
        result.details["brand_schema_score"] = schema_score
        result.details["note"] = (
            "Knowledge Panel eligibility is Google-internal and cannot be directly detected. "
            "This score is derived from Wikipedia presence and Brand schema completeness."
        )

        if derived_score < 50:
            result.recommendations.append(
                "Low Knowledge Panel eligibility. Improve Wikipedia presence and "
                "complete your Organization schema to increase eligibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()