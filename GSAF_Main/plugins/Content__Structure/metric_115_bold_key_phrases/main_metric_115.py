from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.bold_key_phrases import analyze_bold_key_phrases


def run(site_data):

    result = MetricResult(
        factor="15 - Bold Key Phrases"
    )

    try:

        analysis = analyze_bold_key_phrases(
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