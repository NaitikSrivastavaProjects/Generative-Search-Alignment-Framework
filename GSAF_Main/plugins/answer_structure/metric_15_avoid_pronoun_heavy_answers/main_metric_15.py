'''
Avoid Pronoun-Heavy Answers Checker:
Detects whether answer paragraphs overuse pronouns at the start of
sentences instead of repeating the subject.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

PRONOUN_STARTERS = ("it ", "it's", "this ", "that ", "these ", "those ", "they ")

def run(site_data):
    result = MetricResult(factor="15 - Avoid Pronoun-Heavy Answers")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        total_sentences = 0
        pronoun_start_count = 0

        for p in paragraphs:
            text = p.get_text(strip=True)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s_clean = s.strip().lower()
                if not s_clean:
                    continue
                total_sentences += 1
                if s_clean.startswith(PRONOUN_STARTERS):
                    pronoun_start_count += 1

        if total_sentences == 0:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No sentences found"
            return result.to_dict()

        pronoun_ratio = pronoun_start_count / total_sentences
        score = round((1 - pronoun_ratio) * 100)

        result.score = score
        result.status = get_status(score)
        result.details["total_sentences"] = total_sentences
        result.details["pronoun_starting_sentences"] = pronoun_start_count

        if pronoun_ratio > 0.2:
            result.recommendations.append("Replace pronoun-starting sentences (e.g. 'It works by...') with the actual subject.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()