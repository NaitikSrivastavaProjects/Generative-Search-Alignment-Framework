from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.opinion import analyze_opinions


def run(site_data):

    result = MetricResult(
        factor="104 - Strong Opinions & Hot Takes"
    )

    try:

        analysis = analyze_opinions(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()