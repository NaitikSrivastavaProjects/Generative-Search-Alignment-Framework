from datetime import datetime

from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import DATE_KEYWORDS


def run(site_data):

    soup = site_data.soup
    response = site_data.response

    score = 0
    details = {}
    recommendations = []

    page_text = soup.get_text(" ", strip=True).lower()

    # ----------------------------------------
    # 1. Date Keywords (30)
    # ----------------------------------------

    found_keywords = []

    for keyword in DATE_KEYWORDS:
        if keyword.lower() in page_text:
            found_keywords.append(keyword)

    details["date_keywords_found"] = found_keywords

    if len(found_keywords) >= 2:
        score += 30
    elif len(found_keywords) == 1:
        score += 15
    else:
        recommendations.append(
            "Include publication or updated date information."
        )

    # ----------------------------------------
    # 2. <time> Tag (20)
    # ----------------------------------------

    time_tags = soup.find_all("time")

    details["time_tags"] = len(time_tags)

    if len(time_tags) > 0:
        score += 20
    else:
        recommendations.append(
            "Use HTML <time> tags for publication dates."
        )

    # ----------------------------------------
    # 3. Current Year Mention (20)
    # ----------------------------------------

    current_year = str(datetime.now().year)

    if current_year in page_text:
        score += 20
        details["current_year_found"] = True
    else:
        details["current_year_found"] = False
        recommendations.append(
            f"Content does not reference the current year ({current_year})."
        )

    # ----------------------------------------
    # 4. Last-Modified Header (15)
    # ----------------------------------------

    last_modified = response.headers.get("Last-Modified")

    if last_modified:
        score += 15
        details["last_modified"] = last_modified
    else:
        recommendations.append(
            "Server does not provide a Last-Modified HTTP header."
        )

    # ----------------------------------------
    # 5. JSON-LD Date Properties (15)
    # ----------------------------------------

    jsonld_dates = 0

    for item in site_data.json_ld:

        if isinstance(item, dict):

            if "datePublished" in item:
                jsonld_dates += 1

            if "dateModified" in item:
                jsonld_dates += 1

    details["jsonld_date_fields"] = jsonld_dates

    if jsonld_dates > 0:
        score += 15
    else:
        recommendations.append(
            "Add datePublished or dateModified to Schema.org markup."
        )

    return MetricResult(
        factor="Metric 167 - Content Freshness",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()