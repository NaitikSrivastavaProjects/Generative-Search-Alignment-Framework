'''
FAQ Section Checker:
Detects whether the page has a dedicated FAQ section near the bottom
with 3+ question-answer pairs, signaling comprehensiveness to AI engines.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def run(site_data):
    result = MetricResult(factor="8 - FAQ Section at Page Bottom")
    try:
        soup = site_data.soup

        faq_container = soup.find(lambda tag: tag.name in ["section", "div"] and "faq" in tag.get("id", "").lower())
        if not faq_container:
            faq_container = soup.find(lambda tag: tag.name in ["section", "div"] and "faq" in " ".join(tag.get("class", [])).lower())

        all_headings = soup.find_all(["h2", "h3", "h4"])
        question_headings = [h for h in all_headings if _is_question(h.get_text(strip=True))]

        if faq_container:
            qa_pairs = len(faq_container.find_all(["h2", "h3", "h4"]))
            found_via = "explicit FAQ section"
        else:
            midpoint = len(all_headings) // 2
            qa_pairs = len([h for h in question_headings if all_headings.index(h) >= midpoint])
            found_via = "clustered questions near page bottom"

        if qa_pairs >= 3:
            score = 100
        elif qa_pairs > 0:
            score = 50
            result.recommendations.append(f"Only {qa_pairs} FAQ-style Q&A pairs found ({found_via}) — add more to reach at least 3.")
        else:
            score = 0
            result.recommendations.append("Add a dedicated FAQ section near the bottom with at least 3 question-answer pairs.")

        result.score = score
        result.status = get_status(score)
        result.details["qa_pairs_found"] = qa_pairs
        result.details["detection_method"] = found_via

    except Exception as e:
        result.error = str(e)

    return result.to_dict()