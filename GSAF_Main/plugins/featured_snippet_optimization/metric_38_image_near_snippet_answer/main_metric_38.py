'''
Image Near Snippet Answer Checker:
Detects whether a relevant image sits close to the answer paragraph,
increasing the chance of a rich featured snippet with text + image.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="38 - Image Near Snippet Answer")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        first_para = paragraphs[0]
        nearby_img = first_para.find_previous("img") or first_para.find_next("img")

        has_nearby_image = nearby_img is not None
        has_alt_text = bool(nearby_img.get("alt")) if nearby_img else False

        if has_nearby_image and has_alt_text:
            score = 100
        elif has_nearby_image:
            score = 60
            result.recommendations.append("Add descriptive alt text to the image near your answer paragraph.")
        else:
            score = 0
            result.recommendations.append("Add a relevant image close to your main answer paragraph.")

        result.score = score
        result.status = get_status(score)
        result.details["has_nearby_image"] = has_nearby_image
        result.details["has_alt_text"] = has_alt_text

    except Exception as e:
        result.error = str(e)

    return result.to_dict()