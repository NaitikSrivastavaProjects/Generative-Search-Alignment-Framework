from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="72 - Captioned Diagrams")

    try:
        soup = site_data.soup
        figures = soup.find_all("figure")

        if not figures:
            result.status = "Not Applicable"
            result.details["note"] = "No figure elements found on this page."
            return result.to_dict()

        captioned = []
        uncaptioned = []

        for fig in figures:
            figcaption = fig.find("figcaption")
            has_id = bool(fig.get("id"))
            caption_text = figcaption.get_text(strip=True) if figcaption else ""

            if figcaption and len(caption_text.split()) >= 5:
                captioned.append({
                    "caption": caption_text[:80],
                    "has_id": has_id
                })
            else:
                uncaptioned.append(fig.get("id") or "unnamed figure")

        total = len(figures)
        result.details["total_figures"] = total
        result.details["captioned_count"] = len(captioned)
        result.details["uncaptioned_count"] = len(uncaptioned)
        result.details["figures_with_id"] = sum(1 for f in captioned if f["has_id"])

        base_score = round((len(captioned) / total) * 100)
        id_bonus = min(10, result.details["figures_with_id"] * 5)
        result.score = min(100, base_score + id_bonus)
        result.status = get_status(result.score)

        if uncaptioned:
            result.recommendations.append(
                f"{len(uncaptioned)} figure(s) have no proper caption. "
                "Add descriptive figcaption tags to make diagrams eligible for visual answer boxes."
            )

        for block in site_data.json_ld:
            if block.get("@type") == "ImageObject" and block.get("caption"):
                result.details["image_object_schema_found"] = True
                break

    except Exception as e:
        result.error = str(e)

    return result.to_dict()