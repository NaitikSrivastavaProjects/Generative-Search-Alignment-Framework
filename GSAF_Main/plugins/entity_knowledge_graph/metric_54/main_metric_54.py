from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import SAMEAS_PLATFORM_WEIGHTS


def run(site_data):
    result = MetricResult(factor="54 - Entity Linking via sameAs")

    try:
        sameas_links = []

        for block in site_data.json_ld:
            if "sameAs" in block:
                links = block["sameAs"]
                if isinstance(links, str):
                    links = [links]
                sameas_links.extend(links)

        if not sameas_links:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "No sameAs links found in schema markup. "
                "Add sameAs links to Wikipedia, LinkedIn, Crunchbase etc. to strengthen entity signals."
            )
            return result.to_dict()

        total_score = 0
        matched_platforms = []

        for link in sameas_links:
            matched = False
            for platform, weight in SAMEAS_PLATFORM_WEIGHTS.items():
                if platform in link:
                    total_score += weight
                    matched_platforms.append(platform)
                    matched = True
                    break
            if not matched:
                total_score += 2  # unknown links still count a little

        result.details["total_sameas_links"] = len(sameas_links)
        result.details["recognized_platforms"] = matched_platforms
        result.details["sameas_links"] = sameas_links

        result.score = min(100, total_score)
        result.status = get_status(result.score)

        if result.score < 50:
            result.recommendations.append(
                "sameAs links exist but lack high-authority platforms. "
                "Add links to Wikipedia, Wikidata, and LinkedIn for stronger entity confidence."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()