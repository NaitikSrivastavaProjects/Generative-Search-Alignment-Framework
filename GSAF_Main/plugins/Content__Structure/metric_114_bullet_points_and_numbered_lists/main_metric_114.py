from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.list_structure import analyze_list_structure


def run(site_data):

    result = MetricResult(
        factor="114 - Bullet Points & Numbered Lists"
    )

    try:

        analysis = analyze_list_structure(
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