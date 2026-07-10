from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.subheading_density import (
    analyze_subheading_density
)


def run(site_data):

    result = MetricResult(
        factor="16 - Subheading Every 200-300 Words"
    )

    try:

        analysis = analyze_subheading_density(
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