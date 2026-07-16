from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.topic_coverage import analyze_topic_coverage


def run(site_data):

    result = MetricResult(
        factor="110 - Comprehensive Topic Coverage"
    )

    try:

        analysis = analyze_topic_coverage(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()