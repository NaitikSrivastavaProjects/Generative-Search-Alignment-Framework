from models.metric_result import MetricResult
from utils.helpers import get_status


OG_TAGS = {
    "og:title": 25,
    "og:description": 25,
    "og:image": 30,
    "og:url": 20
}


def run(site_data):
    result = MetricResult(factor="99 - Social Validation")

    try:
        soup = site_data.soup
        found_tags = {}

        for tag, points in OG_TAGS.items():
            meta = soup.find("meta", property=tag)
            if meta and meta.get("content", "").strip():
                found_tags[tag] = meta["content"].strip()
                result.score = (result.score or 0) + points

        result.details["og_tags_found"] = found_tags
        result.details["og_tags_missing"] = [t for t in OG_TAGS if t not in found_tags]
        result.status = get_status(result.score)

        if result.details["og_tags_missing"]:
            result.recommendations.append(
                f"Missing Open Graph tags: {', '.join(result.details['og_tags_missing'])}. "
                "These tags control how your page looks when shared on social platforms."
            )

        if "og:image" not in found_tags:
            result.recommendations.append(
                "og:image is missing — links shared without an image get significantly fewer clicks on social platforms."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()