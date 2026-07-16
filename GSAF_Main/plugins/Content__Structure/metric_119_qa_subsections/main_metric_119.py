from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.qa_subsections import analyze_qa_subsections


def run(site_data):

    result = MetricResult(
        factor="119 - Q&A Subsections"
    )

    try:

        analysis = analyze_qa_subsections(
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