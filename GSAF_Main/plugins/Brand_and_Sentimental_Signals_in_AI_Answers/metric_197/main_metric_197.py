import os
import re
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")
 
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
 
NEGATIVE_HEADLINE_KEYWORDS = [
    "lawsuit", "sued", "scandal", "fraud", "investigation", "recall",
    "backlash", "controversy", "outage", "breach", "hack", "layoffs",
    "fined", "penalty", "boycott", "criticized", "slammed", "accused",
    "failure", "collapse", "shutdown", "complaint", "warning", "violation"
]
 
# on-page signals that the brand has publicly addressed negative coverage
CRISIS_RESPONSE_PATTERNS = [
    "official statement", "our response to", "addressing recent",
    "clarification regarding", "in response to recent reports",
    "we take this seriously", "update on the situation", "press statement"
]
 
LOOKBACK_DAYS = 90
 
 
def _extract_brand_name(soup):
    og_site_name = soup.find("meta", attrs={"property": "og:site_name"})
    if og_site_name and og_site_name.get("content"):
        return og_site_name["content"].strip()
 
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if isinstance(block, dict) and block.get("@type") in ("Organization", "Brand"):
                if block.get("name"):
                    return block["name"].strip()
 
    title_tag = soup.find("title")
    return title_tag.get_text(strip=True) if title_tag else None
 
 
def _check_onpage_crisis_response(soup):
    text = soup.get_text(" ", strip=True).lower()
    return any(pattern in text for pattern in CRISIS_RESPONSE_PATTERNS)
 
 
def _query_newsapi(brand_name):
    """Real external check via NewsAPI. Requires NEWSAPI_KEY in .env.
    Returns None if not configured or the request fails, rather than raising --
    callers should treat None as 'unable to verify' and fall back accordingly."""
    if not NEWSAPI_KEY or not brand_name:
        return None
 
    since_date = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
 
    try:
        response = requests.get(
            NEWSAPI_URL,
            params={
                "q": f'"{brand_name}"',
                "from": since_date,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 30,
                "apiKey": NEWSAPI_KEY
            },
            timeout=15
        )
        data = response.json()
        if data.get("status") != "ok":
            return None
 
        articles = data.get("articles", [])
        negative_articles = []
 
        for article in articles:
            headline = (article.get("title") or "").lower()
            description = (article.get("description") or "").lower()
            combined = f"{headline} {description}"
 
            if any(keyword in combined for keyword in NEGATIVE_HEADLINE_KEYWORDS):
                negative_articles.append({
                    "title": article.get("title"),
                    "source": (article.get("source") or {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "url": article.get("url")
                })
 
        return {
            "total_articles_scanned": len(articles),
            "negative_articles_found": negative_articles
        }
 
    except (requests.RequestException, ValueError):
        return None
 
 
def _query_gemini_negative_coverage(brand_name):
    """Fallback only. IMPORTANT LIMITATION: reflects the model's training data cutoff,
    not live news -- it cannot see coverage from recent weeks/months and should only
    be used when no real news API is configured."""
    if not GEMINI_API_KEY or not brand_name:
        return None
 
    prompt = f"""Based on your training data, are you aware of any significant negative news coverage,
controversy, scandal, or crisis associated with the brand/entity "{brand_name}"? Respond ONLY in
valid JSON, no markdown, no preamble.
 
{{
  "aware_of_negative_coverage": true,
  "confidence": "High/Medium/Low",
  "reasoning": "one sentence, no specifics that could be outdated"
}}"""
 
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        raw = response.json()
        text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except Exception as e:
        print(f"Gemini negative coverage lookup error: {e}")
        return None
 
 
def analyze_recent_negative_coverage(site_data):
 
    soup = site_data.soup
    brand_name = _extract_brand_name(soup)
    has_crisis_response = _check_onpage_crisis_response(soup)
 
    news_result = _query_newsapi(brand_name)
    gemini_result = None
 
    data_source = None
    negative_count = 0
 
    if news_result is not None:
        data_source = "newsapi"
        negative_count = len(news_result["negative_articles_found"])
    else:
        gemini_result = _query_gemini_negative_coverage(brand_name)
        if gemini_result is not None:
            data_source = "ai_training_data_estimate"
            negative_count = 1 if gemini_result.get("aware_of_negative_coverage") else 0
 
    if data_source is None:
        # neither a real news API nor the AI fallback was available/configured --
        # cannot assess this metric at all for this run
        score = 50
    elif negative_count == 0:
        score = 90 if data_source == "newsapi" else 70
    else:
        # negative coverage detected -- score inversely to volume, but never
        # below a floor if the brand has visibly addressed it on-page
        base_penalty = min(negative_count, 6) * 12
        score = 90 - base_penalty
        if has_crisis_response:
            score += 15
 
    score = max(0, min(round(score), 100))
 
    details = {
        "brand_name_detected": brand_name,
        "data_source": data_source,
        "onpage_crisis_response_detected": has_crisis_response,
        "negative_articles_found_count": negative_count,
        "negative_articles": news_result["negative_articles_found"] if news_result else [],
        "ai_estimate": gemini_result,
        "lookback_days": LOOKBACK_DAYS if data_source == "newsapi" else None,
        "limitation": (
            "Reliable results require a configured NEWSAPI_KEY for live news search. Without it, this falls "
            "back to the AI model's training data, which cannot see recent coverage and may miss or misjudge "
            "a single high-profile negative article — exactly the failure mode this metric is meant to catch."
        )
    }
 
    recommendations = []
 
    if score < 75:
 
        if data_source is None:
            recommendations.append(
                "Configure a news search API (e.g. NEWSAPI_KEY) to reliably detect recent negative coverage — "
                "this cannot be assessed accurately from the page alone or from AI training data."
            )
 
        if negative_count > 0:
            recommendations.append(
                f"{negative_count} recent article(s) with negative-coverage indicators were found for this brand. "
                "A single high-profile negative article can dominate AI-generated brand answers for months — "
                "consider proactive PR, updated statements, or fresh positive coverage to dilute its prominence."
            )
 
        if negative_count > 0 and not has_crisis_response:
            recommendations.append(
                "No on-page statement addressing the negative coverage was found — publishing a clear, factual "
                "response can give AI engines a balancing, citable source when answering brand-related queries."
            )
 
        if data_source == "ai_training_data_estimate":
            recommendations.append(
                "This result is based on the AI model's training data, not live news — verify manually with a "
                "current news search before drawing conclusions."
            )
 
    return {
        "factor": "Recent Negative Coverage",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_recent_negative_coverage