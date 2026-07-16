from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.tldr_summary import analyze_tldr_summary


def run(site_data):

    result = MetricResult(
        factor="113 - TL;DR Summary at Top"
    )

    try:

        analysis = analyze_tldr_summary(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()