import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from main import run_analysis


app = FastAPI(
    title="Generative Search Alignment Framework API",
    description="SEO, AEO and GEO relevance and ranking engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class AnalyzeRequest(BaseModel):
    url: str
    keyword: Optional[str] = ""
    keywords: Optional[str] = ""
    competitor_url: Optional[str] = ""
    fast_mode: Optional[bool] = True


def map_status(status: str) -> str:
    mapping = {
        "Good": "Good",
        "Average": "Warning",
        "Poor": "Critical",
        "Not Applicable": "Informational",
        "Informational": "Informational",
        "Error": "Error"
    }
    return mapping.get(status, "Informational")


def get_category_from_factor(factor: str) -> str:
    factor_num_str = ''.join(filter(str.isdigit, factor.split('-')[0]))
    try:
        num = int(factor_num_str)
    except ValueError:
        return "Other"

    if 51 <= num <= 60:
        return "Entity & Knowledge Graph"
    elif 61 <= num <= 70:
        return "E-E-A-T & Answer Trust"
    elif 71 <= num <= 78:
        return "Content Format & Multimedia"
    elif 79 <= num <= 89:
        return "Technical Foundations"
    elif 90 <= num <= 95:
        return "Freshness & Maintenance"
    elif 96 <= num <= 100:
        return "Engagement & Behavioral"
    elif 183 <= num <= 196:
        return "Off-Site Webspam"
    return "Other"


def build_assessment(result: dict) -> str:
    score = result.get("score")
    status = result.get("status", "")
    factor = result.get("factor", "")

    if score is None:
        return f"{factor} could not be automatically assessed for this page."
    if score >= 75:
        return f"This metric is performing well with a score of {score}/100."
    if score >= 40:
        return f"This metric needs improvement — current score is {score}/100."
    return f"This metric is critically underperforming at {score}/100 and needs immediate attention."


def build_structured_recommendations(raw_results: list) -> list:
    structured = []
    priority_map = {
        "Critical": "Immediate Fixes",
        "Warning": "High Impact Improvements",
        "Good": "Long-Term Enhancements",
        "Informational": "Long-Term Enhancements"
    }

    for result in raw_results:
        recs = result.get("recommendations", [])
        status = result.get("status", "Informational")
        score = result.get("score")
        factor = result.get("factor", "")

        for rec in recs:
            priority = priority_map.get(map_status(status), "Long-Term Enhancements")
            impact = "High" if status in ("Poor", "Critical") else "Medium" if status in ("Average", "Warning") else "Low"

            structured.append({
                "id": str(uuid.uuid4())[:8],
                "title": factor,
                "description": rec,
                "priority": priority,
                "seo_impact": impact,
                "geo_impact": impact,
                "difficulty": "Easy" if score and score >= 40 else "Hard",
                "business_impact": f"Improving this metric could significantly boost search and AI engine visibility.",
                "suggested_next_action": rec,
                "implementation_details": f"Review and address the issue flagged under {factor}."
            })

    return structured


def build_insights(results: list) -> dict:
    scored = [r for r in results if r.get("score") is not None]
    if not scored:
        return {
            "largest_performance_bottleneck": "Insufficient data",
            "strongest_optimization_area": "Insufficient data",
            "most_impactful_missing_feature": "Run a full audit to identify gaps",
            "highest_authority_signal": "Not determined",
            "weakest_trust_signal": "Not determined"
        }

    worst = min(scored, key=lambda x: x["score"])
    best = max(scored, key=lambda x: x["score"])
    critical = [r for r in scored if r["score"] < 40]
    missing = critical[0]["factor"] if critical else "No critical issues found"

    return {
        "largest_performance_bottleneck": worst["factor"],
        "strongest_optimization_area": best["factor"],
        "most_impactful_missing_feature": missing,
        "highest_authority_signal": best["factor"],
        "weakest_trust_signal": worst["factor"]
    }


@app.get("/")
def root():
    return {"message": "GSAF API is running"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")

    keywords_list = [k.strip() for k in request.keywords.split(",") if k.strip()] if request.keywords else []

    try:
        start = time.time()
        raw_results = run_analysis(
            url=request.url,
            keyword=request.keyword,
            keywords=keywords_list,
            competitor_url=request.competitor_url
        )
        elapsed = round((time.time() - start) * 1000)

        # shape each result to match MetricResult type
        shaped_results = []
        for r in raw_results:
            shaped_results.append({
                "factor": r.get("factor", "Unknown"),
                "score": r.get("score"),
                "status": map_status(r.get("status", "Informational")),
                "category": get_category_from_factor(r.get("factor", "")),
                "assessment": build_assessment(r),
                "recommendations": r.get("recommendations", []),
                "details": r.get("details", {}),
                "execution_time_ms": elapsed
            })

        # calculate overall score from all scored metrics
        scored = [r["score"] for r in shaped_results if r["score"] is not None]
        overall_score = round(sum(scored) / len(scored)) if scored else 0

        # calculate per-category average scores
        category_scores = {}
        category_counts = {}
        for r in shaped_results:
            cat = r["category"]
            if r["score"] is not None:
                category_scores[cat] = category_scores.get(cat, 0) + r["score"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
        categories = {
            cat: round(category_scores[cat] / category_counts[cat])
            for cat in category_scores
        }

        return {
            "url": request.url,
            "keyword": request.keyword,
            "keywords": keywords_list,
            "competitor_url": request.competitor_url or "",
            "overall_score": overall_score,
            "categories": categories,
            "results": shaped_results,
            "insights": build_insights(shaped_results),
            "recommendations": build_structured_recommendations(raw_results),
            "is_fallback": False
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/suggest-competitors")
def suggest_competitors(request: dict):
    # placeholder — can be enhanced later
    url = request.get("url", "")
    return {
        "suggestions": [
            {"url": "competitor1.com", "reasoning": "Similar domain focus and keyword targeting."},
            {"url": "competitor2.com", "reasoning": "Competes in the same search category."},
            {"url": "competitor3.com", "reasoning": "Targets overlapping audience segments."}
        ],
        "is_fallback": True
    }