from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.definition_blocks import analyze_definition_blocks


def run(site_data):

    result = MetricResult(
        factor="17 - Definition Blocks"
    )

    try:

        analysis = analyze_definition_blocks(
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