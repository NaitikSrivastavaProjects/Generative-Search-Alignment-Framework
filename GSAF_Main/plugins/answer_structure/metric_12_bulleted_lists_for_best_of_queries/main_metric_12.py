'''
Bulleted Lists for "Best of" Queries Checker:
Detects whether pages targeting "best of"/listicle queries use unordered
bullet lists.
'''
import re
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="12 - Bulleted Lists for \"Best of\" Queries")
    try:
        soup = site_data.soup
        headings = soup.find_all(["h1", "h2"])
        listicle_headings = [h for h in headings if re.search(r"\bbest\b|\btop\s+\d+\b", h.get_text(strip=True), re.IGNORECASE)]

        if not listicle_headings:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No 'best of'/'top N' style headings found"
            return result.to_dict()

        good_lists = 0
        checked = []
        for heading in listicle_headings:
            heading_text = heading.get_text(strip=True)
            ul = heading.find_next("ul")
            has_bullets = ul is not None and len(ul.find_all("li")) >= 3
            if has_bullets:
                good_lists += 1
            checked.append({"heading": heading_text, "has_bullet_list": has_bullets})

        score = round((good_lists / len(listicle_headings)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["checked"] = checked

        if score < 100:
            result.recommendations.append("Use an unordered <ul> bullet list to present your 'best of'/ranking-style content.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()