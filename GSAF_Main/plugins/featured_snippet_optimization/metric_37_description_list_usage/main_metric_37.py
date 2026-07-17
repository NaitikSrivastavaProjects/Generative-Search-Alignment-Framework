'''
Use of Description Lists Checker:
Detects whether glossary-style content uses HTML description list tags
(dl, dt, dd) to help AI extract term-definition pairs cleanly.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="37 - Use of Description Lists")
    try:
        soup = site_data.soup
        dl_tags = soup.find_all("dl")
        text = soup.get_text().lower()
        looks_like_glossary = "glossary" in text or "definitions" in text or "key terms" in text

        if dl_tags:
            score = 100
        elif looks_like_glossary:
            score = 20
            result.recommendations.append("Page appears glossary-style but doesn't use <dl>/<dt>/<dd> tags — consider adding them.")
        else:
            score = 0

        result.score = score
        result.status = get_status(score)
        result.details["description_lists_found"] = len(dl_tags)
        result.details["looks_like_glossary_content"] = looks_like_glossary

    except Exception as e:
        result.error = str(e)

    return result.to_dict()