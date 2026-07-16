'''
Inverted Pyramid Checker:
Detects whether the most important answer/information appears at the
top of the page rather than buried after long intros or filler.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="3 - Inverted Pyramid Writing")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            result.recommendations.append("Add body paragraphs with the key answer stated early.")
            return result.to_dict()

        first_para_words = len(paragraphs[0].get_text(strip=True).split())
        is_substantive = first_para_words >= 15
        is_concise = first_para_words <= 80

        if is_substantive and is_concise:
            score = 100
        elif not is_substantive:
            score = 30
            result.recommendations.append("First paragraph is too short/thin — lead with a substantive answer, not filler text.")
        else:
            score = 50
            result.recommendations.append("First paragraph is too long — state the core answer within the first 80 words.")

        result.score = score
        result.status = get_status(score)
        result.details["first_paragraph_word_count"] = first_para_words

    except Exception as e:
        result.error = str(e)

    return result.to_dict()