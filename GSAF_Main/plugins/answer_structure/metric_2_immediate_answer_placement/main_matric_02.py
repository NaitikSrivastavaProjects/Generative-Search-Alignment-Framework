'''
Immediate Answer Placement Checker:
Detects whether question-style headings are answered in a 40-60 word
paragraph immediately below them, rather than after long intros.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question_heading(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def run(site_data):
    result = MetricResult(factor="2 - Immediate Answer Placement")
    try:
        soup = site_data.soup
        question_headings = [h for h in soup.find_all(["h1", "h2"]) if _is_question_heading(h.get_text(strip=True))]

        if not question_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No question-style headings found to check"
            result.recommendations.append("Add question-style H1/H2 headings first, then place a direct answer below each.")
            return result.to_dict()

        good_placements = 0
        checked = []

        for heading in question_headings:
            heading_text = heading.get_text(strip=True)
            next_para = heading.find_next_sibling("p")
            if next_para:
                word_count = len(next_para.get_text(strip=True).split())
                in_range = 40 <= word_count <= 60
                if in_range:
                    good_placements += 1
                else:
                    result.recommendations.append(f"Answer under \"{heading_text}\" is {word_count} words — tighten to 40-60 words.")
                checked.append({"heading": heading_text, "word_count": word_count, "in_range": in_range})
            else:
                result.recommendations.append(f"No paragraph directly follows heading: \"{heading_text}\"")
                checked.append({"heading": heading_text, "word_count": 0, "in_range": False})

        score = round((good_placements / len(question_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["checked_headings"] = checked

    except Exception as e:
        result.error = str(e)

    return result.to_dict()