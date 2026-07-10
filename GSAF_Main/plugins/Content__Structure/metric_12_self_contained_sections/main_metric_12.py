from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.self_contained_sections import (
    analyze_self_contained_sections
)


def run(site_data):

    result = MetricResult(
        factor="12 - Self-Contained Sections"
    )

    try:

        analysis = analyze_self_contained_sections(
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