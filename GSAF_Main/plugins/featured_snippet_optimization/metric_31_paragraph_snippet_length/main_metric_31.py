'''
Paragraph Snippet Length Checker:
Detects whether answer paragraphs are 40-60 words long — the sweet
spot AI engines extract cleanly as a snippet.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="31 - Paragraph Snippet Length")
    try:
        paragraphs = site_data.soup.find_all("p")
        if not paragraphs:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No paragraph content found"
            return result.to_dict()

        in_range_count = 0
        checked = []
        for p in paragraphs:
            word_count = len(p.get_text(strip=True).split())
            if word_count == 0:
                continue
            in_range = 40 <= word_count <= 60
            if in_range:
                in_range_count += 1
            checked.append({"word_count": word_count, "in_range": in_range})

        if not checked:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No non-empty paragraphs found"
            return result.to_dict()

        ratio = in_range_count / len(checked)
        score = round(ratio * 100)

        result.score = score
        result.status = get_status(score)
        result.details["total_paragraphs"] = len(checked)
        result.details["paragraphs_in_range"] = in_range_count

        if score < 40:
            result.recommendations.append("Rewrite key answer paragraphs to be 40-60 words long for better snippet extraction.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()