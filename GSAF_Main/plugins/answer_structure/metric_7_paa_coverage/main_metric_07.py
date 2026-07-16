'''
People Also Ask (PAA) Coverage Checker:
Detects how many distinct related questions a page answers, since
broader question coverage increases the chance of being picked for
multiple different AI queries.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def run(site_data):
    result = MetricResult(factor="7 - People Also Ask (PAA) Coverage")
    try:
        headings = site_data.soup.find_all(["h1", "h2", "h3"])
        questions = [h.get_text(strip=True) for h in headings if _is_question(h.get_text(strip=True))]
        unique_questions = list(dict.fromkeys(questions))

        count = len(unique_questions)
        if count == 0:
            score = 0
            result.recommendations.append("Add multiple distinct question-style headings covering related sub-topics.")
        elif count == 1:
            score = 40
            result.recommendations.append("Only one question covered — add more related questions to widen AI answer coverage.")
        elif count <= 3:
            score = 70
            result.recommendations.append("Consider adding a few more related questions for broader coverage.")
        else:
            score = 100

        result.score = score
        result.status = get_status(score)
        result.details["distinct_questions_found"] = count
        result.details["questions"] = unique_questions[:10]

    except Exception as e:
        result.error = str(e)

    return result.to_dict()