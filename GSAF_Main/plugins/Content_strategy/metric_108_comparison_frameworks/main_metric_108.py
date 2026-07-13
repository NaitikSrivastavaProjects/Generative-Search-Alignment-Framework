from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.comparison_framework import analyze_comparison_framework


def run(site_data):

    result = MetricResult(
        factor="08 - Comparison Frameworks"
    )

    try:

        analysis = analyze_comparison_framework(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()