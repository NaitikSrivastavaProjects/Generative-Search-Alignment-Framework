'''
Long-Tail Question Targeting Checker:
Detects whether headings are long-tail, specific questions (5-10 words)
rather than short 1-2 word keyword-style headings.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="6 - Long-Tail Question Targeting")
    try:
        headings = site_data.soup.find_all(["h1", "h2"])

        if not headings:
            result.score = 0
            result.status = get_status(0)
            result.details["total_headings"] = 0
            result.recommendations.append("Add H1/H2 headings phrased as specific, longer questions.")
            return result.to_dict()

        long_tail_count = 0
        checked = []
        for heading in headings:
            text = heading.get_text(strip=True)
            word_count = len(text.split())
            is_long_tail = 5 <= word_count <= 10
            if is_long_tail:
                long_tail_count += 1
            checked.append({"heading": text, "word_count": word_count, "is_long_tail": is_long_tail})

        score = round((long_tail_count / len(headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["total_headings"] = len(headings)
        result.details["long_tail_headings"] = long_tail_count
        result.details["checked"] = checked

        if score < 60:
            result.recommendations.append("Expand short keyword-style headings into full 5-10 word questions matching how users actually ask AI.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()