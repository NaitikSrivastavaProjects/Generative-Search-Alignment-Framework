import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from models.metric_result import MetricResult
from utils.helpers import get_status

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_KEY = os.getenv("PAGESPEED_API_KEY")


def run(site_data):
    result = MetricResult(factor="82 - Mobile Responsiveness")

    if not API_KEY:
        result.error = "PageSpeed API key not configured"
        return result.to_dict()

    try:
        soup = site_data.soup

        viewport_tag = soup.find("meta", attrs={"name": "viewport"})
        has_viewport = bool(viewport_tag and "width=device-width" in viewport_tag.get("content", ""))

        result.details["viewport_tag_found"] = has_viewport
        result.details["viewport_content"] = viewport_tag.get("content", "") if viewport_tag else None

        response = requests.get(
            PAGESPEED_API,
            params={"url": site_data.url, "key": API_KEY, "strategy": "mobile"},
            timeout=30
        )
        data = response.json()

        mobile_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", None)

        if mobile_score is not None:
            mobile_score = round(mobile_score * 100)
            result.details["pagespeed_mobile_score"] = mobile_score
        else:
            mobile_score = 50

        viewport_score = 50 if has_viewport else 0
        result.score = min(100, viewport_score + round(mobile_score / 2))
        result.status = get_status(result.score)

        if not has_viewport:
            result.recommendations.append(
                "Viewport meta tag missing — add "
                "<meta name='viewport' content='width=device-width, initial-scale=1'> "
                "to enable mobile-first indexing."
            )

        if mobile_score < 50:
            result.recommendations.append(
                f"Mobile PageSpeed score is {mobile_score}/100. "
                "Optimize for mobile — compress images, reduce render-blocking scripts."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()