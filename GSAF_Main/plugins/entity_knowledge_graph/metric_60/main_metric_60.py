from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="60 - Disambiguation Pages")

    try:
        ai_data = site_data.ai_results.get("metric_60", {})

        if not ai_data:
            result.score = 50
            result.status = "Average"
            result.details["note"] = "AI batch result not available — cannot assess disambiguation."
            return result.to_dict()

        disambiguates = ai_data.get("disambiguates", False)
        reasoning = ai_data.get("reasoning", "")

        result.details["disambiguates"] = disambiguates
        result.details["ai_reasoning"] = reasoning

        result.score = 100 if disambiguates else 0
        result.status = get_status(result.score)

        if not disambiguates:
            result.recommendations.append(
                "Content does not explicitly clarify which entity it refers to. "
                "If your brand/topic name is ambiguous, add a clear disambiguation statement early in the content."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()