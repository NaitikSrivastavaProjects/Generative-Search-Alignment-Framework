from urllib.parse import urlparse
from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="75 - Original Charts and Infographics")

    try:
        soup = site_data.soup
        domain = site_data.domain

        canvas_elements = soup.find_all("canvas")
        svg_elements = soup.find_all("svg")

        same_domain_images = [
            img for img in soup.find_all("img", src=True)
            if domain in img["src"] or img["src"].startswith("/")
        ]

        image_schema = [
            b for b in site_data.json_ld
            if b.get("@type") == "ImageObject"
        ]

        result.details["canvas_elements"] = len(canvas_elements)
        result.details["svg_elements"] = len(svg_elements)
        result.details["same_domain_images"] = len(same_domain_images)
        result.details["image_schema_found"] = len(image_schema)

        if canvas_elements or svg_elements:
            result.score = 100
        elif image_schema:
            result.score = 80
        elif same_domain_images:
            result.score = 60
        else:
            result.score = 20
            result.recommendations.append(
                "No original visual content signals detected. "
                "Add original charts, SVGs, or infographics to improve answer box eligibility."
            )

        result.status = get_status(result.score)
        result.details["limitation"] = (
            "True image originality cannot be verified from HTML alone. "
            "This score reflects presence of original visual content signals only."
        )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()