'''
Snippet Bait Paragraphs Checker:
Detects whether the page has a dedicated, self-contained answer block
near the top that answers the query without needing surrounding context.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="34 - Snippet Bait Paragraphs")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        top_paragraphs = paragraphs[:3]
        best_candidate = None
        for p in top_paragraphs:
            text = p.get_text(strip=True)
            word_count = len(text.split())
            starts_with_pronoun = text.lower().startswith(("it ", "this ", "that ", "these ", "those "))
            is_substantial = 30 <= word_count <= 70
            if is_substantial and not starts_with_pronoun:
                best_candidate = {"text_preview": text[:100], "word_count": word_count}
                break

        if best_candidate:
            score = 100
        else:
            score = 30
            result.recommendations.append("Add a self-contained 30-70 word answer paragraph near the top that doesn't rely on preceding context or pronouns.")

        result.score = score
        result.status = get_status(score)
        result.details["best_candidate"] = best_candidate

    except Exception as e:
        result.error = str(e)

    return result.to_dict()