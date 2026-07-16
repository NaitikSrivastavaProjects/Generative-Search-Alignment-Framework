from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.expert_quotes import analyze_expert_quotes


def run(site_data):

    result = MetricResult(
        factor="105 - Expert Quotes"
    )

    try:

        analysis = analyze_expert_quotes(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()