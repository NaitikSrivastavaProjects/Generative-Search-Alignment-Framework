'''
Direct Question Heading Checker:
Detects whether a page's H1/H2 headings are phrased as direct questions,
since AI search engines favor content clearly structured to answer a query.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def run(site_data):
    result = MetricResult(factor="1 - Direct Question in H1/H2")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])

        if not headings:
            result.score = 0
            result.status = get_status(0)
            result.details["total_headings"] = 0
            result.recommendations.append("Add at least one H1/H2 heading.")
            return result.to_dict()

        question_headings = []
        for heading in headings:
            text = heading.get_text(strip=True).lower()
            if text.endswith("?") or text.startswith(QUESTION_STARTERS):
                question_headings.append(heading.get_text(strip=True))

        ratio = len(question_headings) / len(headings)
        score = round(ratio * 100)

        result.score = score
        result.status = get_status(score)
        result.details["total_headings"] = len(headings)
        result.details["question_headings_found"] = len(question_headings)
        result.details["examples"] = question_headings[:5]

        if not question_headings:
            result.recommendations.append("Phrase at least one H1/H2 as a direct question, e.g. 'What is Machine Learning?'")
        elif ratio < 0.5:
            result.recommendations.append("Phrase more of your headings as direct questions to improve AI answer targeting.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()