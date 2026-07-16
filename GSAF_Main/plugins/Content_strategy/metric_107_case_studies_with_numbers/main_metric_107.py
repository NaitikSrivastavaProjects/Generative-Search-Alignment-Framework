from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.case_study import analyze_case_studies


def run(site_data):

    result = MetricResult(
        factor="107 - Case Studies with Numbers"
    )

    try:

        analysis = analyze_case_studies(site_data)

        result.score = analysis["score"]

        result.status = get_status(result.score)

        result.details = analysis["details"]

        result.recommendations = analysis["recommendations"]

    except Exception as e:

        result.error = str(e)

    return result.to_dict()