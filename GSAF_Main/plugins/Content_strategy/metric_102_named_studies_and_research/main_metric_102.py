from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.research import analyze_research


def run(site_data):

    result = MetricResult(
        factor="102 - Named Studies & Research"
    )

    try:

        analysis = analyze_research(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()