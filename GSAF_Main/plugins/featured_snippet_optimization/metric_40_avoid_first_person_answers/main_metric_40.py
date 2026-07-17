'''
Avoid First-Person in Answers Checker:
Detects whether answer sentences use first-person/opinion phrasing
instead of impersonal, factual voice.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

FIRST_PERSON_PHRASES = ("we think", "we believe", "in our opinion", "i think", "i believe", "in my opinion", "we feel")

def run(site_data):
    result = MetricResult(factor="40 - Avoid First-Person in Answers")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

        if not sentences:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No sentences found"
            return result.to_dict()

        first_person_count = sum(1 for s in sentences if any(phrase in s.lower() for phrase in FIRST_PERSON_PHRASES))
        ratio = first_person_count / len(sentences)
        score = round((1 - ratio) * 100)

        result.score = score
        result.status = get_status(score)
        result.details["total_sentences"] = len(sentences)
        result.details["first_person_sentences"] = first_person_count

        if first_person_count > 0:
            result.recommendations.append('Replace first-person/opinion phrasing (e.g. "we think") with factual statements (e.g. "Machine learning is...").')

    except Exception as e:
        result.error = str(e)

    return result.to_dict()