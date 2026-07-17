'''
Question in H2/H3, Answer in Paragraph Below Checker:
Detects the classic snippet-winning pattern — a question subheading
immediately followed by a direct answer paragraph.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question_heading(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def run(site_data):
    result = MetricResult(factor="35 - Question in H2/H3, Answer in Paragraph Below")
    try:
        headings = site_data.soup.find_all(["h2", "h3"])
        question_headings = [h for h in headings if _is_question_heading(h.get_text(strip=True))]

        if not question_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No question-style H2/H3 headings found"
            result.recommendations.append("Add H2/H3 headings phrased as questions, followed immediately by answer paragraphs.")
            return result.to_dict()

        good_pattern_count = 0
        for heading in question_headings:
            next_para = heading.find_next_sibling("p")
            if next_para and len(next_para.get_text(strip=True).split()) > 0:
                good_pattern_count += 1

        score = round((good_pattern_count / len(question_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["total_question_headings"] = len(question_headings)
        result.details["headings_with_answer_below"] = good_pattern_count

        if score < 100:
            result.recommendations.append("Ensure every question-style H2/H3 heading is immediately followed by an answer paragraph.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()