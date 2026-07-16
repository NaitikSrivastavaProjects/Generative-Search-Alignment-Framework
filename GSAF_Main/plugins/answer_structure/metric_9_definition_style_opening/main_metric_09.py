'''
Definition-Style Opening Sentence Checker:
For "What is X" style headings, detects whether the first sentence of
the answer follows the "[Term] is..." definitional pattern.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def _extract_term(heading_text):
    match = re.search(r"what\s+(?:is|are)\s+(.+?)\??$", heading_text.strip(), re.IGNORECASE)
    return match.group(1).strip() if match else None

def run(site_data):
    result = MetricResult(factor="9 - Definition-Style Opening Sentences")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])
        what_is_headings = [h for h in headings if re.match(r"what\s+(is|are)\s+", h.get_text(strip=True), re.IGNORECASE)]

        if not what_is_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No 'What is...' style headings found"
            result.recommendations.append("Add a 'What is [Term]?' heading if this page targets definitional queries.")
            return result.to_dict()

        good_definitions = 0
        checked = []
        for heading in what_is_headings:
            heading_text = heading.get_text(strip=True)
            term = _extract_term(heading_text)
            next_para = heading.find_next_sibling("p")
            follows_pattern = False
            if next_para and term:
                first_sentence = next_para.get_text(strip=True).split(".")[0]
                if re.match(rf"^{re.escape(term)}\s+(is|are)\b", first_sentence, re.IGNORECASE):
                    follows_pattern = True
            if follows_pattern:
                good_definitions += 1
            checked.append({"heading": heading_text, "term": term, "follows_pattern": follows_pattern})

        score = round((good_definitions / len(what_is_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["checked"] = checked

        if score < 100:
            result.recommendations.append('Start the answer paragraph with "[Term] is..." immediately after "What is [Term]?" headings.')

    except Exception as e:
        result.error = str(e)

    return result.to_dict()