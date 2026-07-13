from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.structured_tables import analyze_structured_tables


def run(site_data):

    result = MetricResult(
        factor="18 - Structured Comparison Tables"
    )

    try:

        analysis = analyze_structured_tables(
            site_data
        )

        result.score = analysis["score"]

        result.status = get_status(
            result.score
        )

        result.details = analysis["details"]

        result.recommendations = analysis[
            "recommendations"
        ]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()