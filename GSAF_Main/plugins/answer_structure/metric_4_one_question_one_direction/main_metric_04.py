'''
One Question One Direction Checker:
Detects whether each heading covers a single topic/question rather than
mixing multiple questions or ideas under one heading.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question_heading(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def run(site_data):
    result = MetricResult(factor="4 - One Question, One Direction")
    try:
        soup = site_data.soup
        question_headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2"]) if _is_question_heading(h.get_text(strip=True))]

        if not question_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No question-style headings found to check"
            result.recommendations.append("Add question-style H1/H2 headings first.")
            return result.to_dict()

        clean_count = 0
        for text in question_headings:
            if text.count("?") > 1 or " and " in text.lower():
                result.recommendations.append(f"Split multi-part heading into separate headings: \"{text}\"")
            else:
                clean_count += 1

        score = round((clean_count / len(question_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["total_question_headings"] = len(question_headings)
        result.details["clean_headings"] = clean_count

    except Exception as e:
        result.error = str(e)

    return result.to_dict()