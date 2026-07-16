from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.quotable import analyze_quotable_insights


def run(site_data):

    result = MetricResult(
        factor="103 - Quotable Insights"
    )

    try:

        analysis = analyze_quotable_insights(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()