from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.experience import analyze_first_hand_experience


def run(site_data):

    result = MetricResult(
        factor="06 - First-Hand Experience"
    )

    try:

        analysis = analyze_first_hand_experience(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()