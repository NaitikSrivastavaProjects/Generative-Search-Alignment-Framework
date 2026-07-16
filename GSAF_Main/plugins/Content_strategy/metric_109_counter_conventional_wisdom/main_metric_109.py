from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.counter_conventional import analyze_counter_conventional


def run(site_data):

    result = MetricResult(
        factor="109 - Counter Conventional Wisdom"
    )

    try:

        analysis = analyze_counter_conventional(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()