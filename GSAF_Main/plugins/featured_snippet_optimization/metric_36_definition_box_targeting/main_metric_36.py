'''
Definition Box Targeting Checker:
Detects whether the first sentence of the content is a clean "X is Y"
definition — the most commonly extracted format for definition snippets.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="36 - Definition Box Targeting")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        first_para = paragraphs[0].get_text(strip=True)
        first_sentence = re.split(r'(?<=[.!?])\s+', first_para)[0] if first_para else ""

        matches_pattern = bool(re.match(r"^[A-Z][\w\s\-]{1,40}\s+(is|are)\s+\w+", first_sentence))

        score = 100 if matches_pattern else 20
        result.score = score
        result.status = get_status(score)
        result.details["first_sentence"] = first_sentence

        if not matches_pattern:
            result.recommendations.append('Rewrite the opening sentence to follow the "[Term] is [definition]" pattern.')

    except Exception as e:
        result.error = str(e)

    return result.to_dict()