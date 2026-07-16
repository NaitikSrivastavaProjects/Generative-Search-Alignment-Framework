'''
Plain Language Over Jargon Checker:
Approximates readability by checking average sentence length and
average word length as a proxy for jargon-heavy vs. plain-language content.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="14 - Plain Language Over Jargon")
    try:
        paragraphs = site_data.soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)

        if not text.strip():
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No body text found"
            return result.to_dict()

        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()

        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

        good_sentence_length = avg_sentence_length <= 20
        good_word_length = avg_word_length <= 5.5

        if good_sentence_length and good_word_length:
            score = 100
        elif good_sentence_length or good_word_length:
            score = 60
            result.recommendations.append("Simplify sentence structure and reduce jargon/long words further.")
        else:
            score = 30
            result.recommendations.append("Rewrite using shorter sentences and everyday vocabulary instead of technical jargon.")

        result.score = score
        result.status = get_status(score)
        result.details["avg_sentence_length_words"] = round(avg_sentence_length, 1)
        result.details["avg_word_length_chars"] = round(avg_word_length, 1)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()