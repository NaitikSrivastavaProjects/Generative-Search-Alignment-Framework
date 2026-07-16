'''
Step-by-Step List Checker:
For "How to" style content, detects whether steps are presented as a
numbered/ordered list with 3+ steps.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="10 - Step-by-Step Lists for How Queries")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])
        how_to_headings = [h for h in headings if re.match(r"how\s+(to|do|can)\b", h.get_text(strip=True), re.IGNORECASE)]

        if not how_to_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No 'How to...' style headings found"
            result.recommendations.append("Add a 'How to...' heading if this page targets instructional queries.")
            return result.to_dict()

        good_lists = 0
        checked = []
        for heading in how_to_headings:
            heading_text = heading.get_text(strip=True)
            ol = heading.find_next("ol")
            step_count = len(ol.find_all("li")) if ol else 0
            has_steps = step_count >= 3
            if has_steps:
                good_lists += 1
            checked.append({"heading": heading_text, "step_count": step_count, "has_ordered_list": has_steps})

        score = round((good_lists / len(how_to_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["checked"] = checked

        if score < 100:
            result.recommendations.append("Convert how-to content into a numbered <ol> list with at least 3 clear steps.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()