from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.semantic_html import analyze_semantic_html


def run(site_data):

    result = MetricResult(
        factor="11 - Clear Semantic HTML"
    )

    try:

        analysis = analyze_semantic_html(
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