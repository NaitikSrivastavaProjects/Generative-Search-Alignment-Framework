'''
Snippet Hijacking via Better Format Checker:
Scores the page's overall snippet-readiness (word count, list/table
structure, definition clarity) as a composite.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="39 - Snippet Hijacking via Better Format")
    try:
        soup = site_data.soup
        paragraphs = soup.find_all("p")
        lists = soup.find_all(["ul", "ol"])
        tables = soup.find_all("table")

        first_para_words = len(paragraphs[0].get_text(strip=True).split()) if paragraphs else 0
        good_para_length = 40 <= first_para_words <= 60

        has_structured_content = len(lists) > 0 or len(tables) > 0

        first_sentence = ""
        if paragraphs:
            text = paragraphs[0].get_text(strip=True)
            first_sentence = re.split(r'(?<=[.!?])\s+', text)[0] if text else ""
        clean_definition = bool(re.match(r"^[A-Z][\w\s\-]{1,40}\s+(is|are)\s+\w+", first_sentence))

        factors_met = sum([good_para_length, has_structured_content, clean_definition])
        score = round((factors_met / 3) * 100)

        result.score = score
        result.status = get_status(score)
        result.details["good_paragraph_length"] = good_para_length
        result.details["has_structured_content"] = has_structured_content
        result.details["clean_definition_opening"] = clean_definition

        if not good_para_length:
            result.recommendations.append("Tighten your main answer paragraph to 40-60 words.")
        if not has_structured_content:
            result.recommendations.append("Add a list or table to strengthen structure over competitor pages.")
        if not clean_definition:
            result.recommendations.append('Open with a clean "[Term] is..." definition sentence.')

    except Exception as e:
        result.error = str(e)

    return result.to_dict()