from models.metric_result import MetricResult
from utils.helpers import get_status


def normalize_url(url):
    return url.rstrip("/").replace("http://", "https://").replace("//www.", "//")


def run(site_data):
    result = MetricResult(factor="87 - Canonical Consistency")

    try:
        soup = site_data.soup
        current_url = site_data.url

        canonical_tag = soup.find("link", rel="canonical")

        if not canonical_tag:
            result.score = 30
            result.status = get_status(result.score)
            result.details["canonical_found"] = False
            result.recommendations.append(
                "No canonical tag found — add one to prevent duplicate content issues."
            )
            return result.to_dict()

        canonical_url = canonical_tag.get("href", "").strip()
        result.details["canonical_found"] = True
        result.details["canonical_url"] = canonical_url
        result.details["current_url"] = current_url

        if normalize_url(canonical_url) == normalize_url(current_url):
            result.score = 100
        else:
            # identify the type of mismatch
            if canonical_url.replace("http://", "https://") == current_url:
                mismatch = "HTTP vs HTTPS"
            elif canonical_url.rstrip("/") == current_url.rstrip("/"):
                mismatch = "Trailing slash"
            elif canonical_url.replace("//www.", "//") == current_url.replace("//www.", "//"):
                mismatch = "www vs non-www"
            else:
                mismatch = "Different URL"

            result.details["mismatch_type"] = mismatch
            result.score = 50
            result.recommendations.append(
                f"Canonical URL mismatch ({mismatch}) — canonical points to a different URL than the current page. "
                "Ensure the canonical tag matches the intended primary URL exactly."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()