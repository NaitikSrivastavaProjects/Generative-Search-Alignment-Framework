import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from models.metric_result import MetricResult
from utils.helpers import get_status

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_KEY = os.getenv("PAGESPEED_API_KEY")


def get_cwv_score(value, good_threshold, poor_threshold):
    if value <= good_threshold:
        return 100
    if value <= poor_threshold:
        return 50
    return 0


def run(site_data):
    result = MetricResult(factor="81 - Fast Core Web Vitals")

    if not API_KEY:
        result.error = "PageSpeed API key not configured"
        return result.to_dict()

    try:
        response = requests.get(
            PAGESPEED_API,
            params={"url": site_data.url, "key": API_KEY, "strategy": "mobile"},
            timeout=30
        )
        data = response.json()

        metrics = data.get("lighthouseResult", {}).get("audits", {})
        cwv = data.get("loadingExperience", {}).get("metrics", {})

        lcp = cwv.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile", None)
        inp = cwv.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile", None)
        cls = cwv.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile", None)

        result.details["lcp_ms"] = lcp
        result.details["inp_ms"] = inp
        result.details["cls"] = cls / 100 if cls else None

        scores = []

        if lcp:
            lcp_score = get_cwv_score(lcp, 2500, 4000)
            result.details["lcp_score"] = lcp_score
            scores.append(lcp_score)
            if lcp_score < 100:
                result.recommendations.append(
                    f"LCP is {lcp}ms — should be under 2500ms. "
                    "Optimize images, server response time, and render-blocking resources."
                )

        if inp:
            inp_score = get_cwv_score(inp, 200, 500)
            result.details["inp_score"] = inp_score
            scores.append(inp_score)
            if inp_score < 100:
                result.recommendations.append(
                    f"INP is {inp}ms — should be under 200ms. "
                    "Reduce JavaScript execution time and long tasks."
                )

        if cls is not None:
            cls_val = cls / 100
            cls_score = get_cwv_score(cls_val, 0.1, 0.25)
            result.details["cls_score"] = cls_score
            scores.append(cls_score)
            if cls_score < 100:
                result.recommendations.append(
                    f"CLS is {cls_val} — should be under 0.1. "
                    "Set explicit dimensions on images and avoid inserting content above existing content."
                )

        if scores:
            result.score = round(sum(scores) / len(scores))
        else:
            result.score = 50
            result.details["note"] = "Field data not available — lab data used as fallback."

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()