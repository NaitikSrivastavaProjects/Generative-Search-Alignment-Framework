import re
from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="89 - max-snippet Meta Tag")

    try:
        soup = site_data.soup

        robot_tags = soup.find_all("meta", attrs={"name": re.compile(r"^(robots|googlebot)$", re.I)})

        if not robot_tags:
            result.score = 100
            result.status = "Good"
            result.details["max_snippet_value"] = "absent (defaults to unlimited)"
            return result.to_dict()

        result.details["tag_found"] = True

        for tag in robot_tags:
            content = tag.get("content", "").lower()

            if "nosnippet" in content:
                result.score = 0
                result.details["max_snippet_value"] = "nosnippet"
                result.recommendations.append(
                    "nosnippet is set — page is completely opted out of answer boxes. "
                    "Remove this directive to restore answer box eligibility."
                )
                break

            match = re.search(r"max-snippet:\s*(-?\d+)", content)
            if match:
                value = int(match.group(1))
                result.details["max_snippet_value"] = value

                if value == -1:
                    result.score = 100
                elif value == 0:
                    result.score = 0
                    result.recommendations.append(
                        "max-snippet:0 disables snippet extraction entirely. "
                        "Set to max-snippet:-1 to allow full answer box eligibility."
                    )
                else:
                    result.score = min(80, value // 2)
                    result.recommendations.append(
                        f"max-snippet is limited to {value} characters. "
                        "Set max-snippet:-1 to allow full extraction for answer boxes."
                    )
                break
            else:
                result.score = 100
                result.details["max_snippet_value"] = "not set (defaults to unlimited)"

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()