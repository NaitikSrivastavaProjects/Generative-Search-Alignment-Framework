import os
import re
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
 
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")
 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
 
 
POSITIVE_LEXICON = [
    "excellent", "amazing", "great", "love", "best", "outstanding", "fantastic",
    "helpful", "reliable", "trustworthy", "recommend", "impressed", "satisfied",
    "exceeded expectations", "highly recommend", "wonderful"
]
 
NEGATIVE_LEXICON = [
    "terrible", "awful", "worst", "hate", "disappointing", "unreliable",
    "scam", "avoid", "poor service", "waste of money", "never again",
    "horrible", "frustrated", "complaint", "refund", "unacceptable"
]
 
REVIEW_SECTION_PATTERNS = ["review", "testimonial", "what our customers say", "customer feedback"]
 
 
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
 
 
def _extract_aggregate_rating(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            rating = block.get("aggregateRating")
            if isinstance(rating, dict) and rating.get("ratingValue"):
                try:
                    return {
                        "rating_value": float(rating["ratingValue"]),
                        "best_rating": float(rating.get("bestRating", 5)),
                        "review_count": int(rating.get("reviewCount") or rating.get("ratingCount") or 0)
                    }
                except (TypeError, ValueError):
                    continue
    return None
 
 
def _scan_onpage_review_sentiment(soup):
    text = soup.get_text(" ", strip=True).lower()
 
    positive_hits = sum(text.count(phrase) for phrase in POSITIVE_LEXICON)
    negative_hits = sum(text.count(phrase) for phrase in NEGATIVE_LEXICON)
 
    has_review_section = any(pattern in text for pattern in REVIEW_SECTION_PATTERNS)
 
    return {
        "positive_mentions": positive_hits,
        "negative_mentions": negative_hits,
        "has_review_or_testimonial_section": has_review_section
    }
 
 
def _query_gemini_sentiment(brand_name):
    """Best-effort supplementary signal. IMPORTANT LIMITATION: without search grounding
    enabled on the API call, this reflects the model's training data, not live web
    sentiment -- treat it as directional context only, not a substitute for real
    aggregate monitoring (e.g. metric 100's direct AI-answer monitoring)."""
    if not GEMINI_API_KEY or not brand_name:
        return None
 
    prompt = f"""Based on your general knowledge, what is the broad public/online sentiment reputation
associated with the brand or entity "{brand_name}"? Respond ONLY in valid JSON, no markdown, no preamble.
 
{{
  "net_sentiment": "Positive/Mixed/Negative/Unknown",
  "confidence": "High/Medium/Low",
  "reasoning": "one sentence"
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
        print(f"Gemini sentiment lookup error: {e}")
        return None
 
 
def analyze_net_sentiment(site_data):
 
    soup = site_data.soup
 
    brand_name = _extract_brand_name(soup)
    aggregate_rating = _extract_aggregate_rating(soup)
    onpage_sentiment = _scan_onpage_review_sentiment(soup)
 
    # reuse a cached ai_batch result if the orchestrator already stored one for this
    # metric, so we don't fire a duplicate Gemini call within the same analysis run
    ai_results = getattr(site_data, "ai_results", {}) or {}
    gemini_sentiment = ai_results.get("metric_96")
    if gemini_sentiment is None:
        gemini_sentiment = _query_gemini_sentiment(brand_name)
 
    score = 0
    signals_used = []
 
    if aggregate_rating and aggregate_rating["review_count"] > 0:
        normalized = (aggregate_rating["rating_value"] / aggregate_rating["best_rating"]) * 100
        score += normalized * 0.6
        score += min(aggregate_rating["review_count"], 100) / 100 * 10
        signals_used.append("aggregate_rating_schema")
 
    onpage_net = onpage_sentiment["positive_mentions"] - onpage_sentiment["negative_mentions"]
    if onpage_sentiment["positive_mentions"] or onpage_sentiment["negative_mentions"]:
        onpage_component = 50 + max(-50, min(50, onpage_net * 8))
        score += onpage_component * 0.25 if aggregate_rating else onpage_component * 0.5
        signals_used.append("onpage_review_lexicon")
 
    if gemini_sentiment and gemini_sentiment.get("net_sentiment"):
        sentiment_map = {"Positive": 90, "Mixed": 55, "Negative": 15, "Unknown": 50}
        gemini_component = sentiment_map.get(gemini_sentiment["net_sentiment"], 50)
        weight = 0.15 if signals_used else 0.6
        score += gemini_component * weight
        signals_used.append("ai_general_knowledge_estimate")
 
    if not signals_used:
        score = 50  # no sentiment signal available at all -- neutral, not penalized
 
    score = max(0, min(round(score), 100))
 
    details = {
        "brand_name_detected": brand_name,
        "aggregate_rating": aggregate_rating,
        "onpage_positive_mentions": onpage_sentiment["positive_mentions"],
        "onpage_negative_mentions": onpage_sentiment["negative_mentions"],
        "has_review_or_testimonial_section": onpage_sentiment["has_review_or_testimonial_section"],
        "ai_estimated_sentiment": gemini_sentiment.get("net_sentiment") if gemini_sentiment else None,
        "ai_estimate_confidence": gemini_sentiment.get("confidence") if gemini_sentiment else None,
        "ai_estimate_reasoning": gemini_sentiment.get("reasoning") if gemini_sentiment else None,
        "signals_used": signals_used,
        "limitation": (
            "This score is a proxy built from on-page signals and/or the AI model's training data. "
            "It does not perform live aggregation of review sites, social media, or news sentiment across "
            "the web, so it should be treated as directional rather than a precise net-sentiment measurement."
        )
    }
 
    recommendations = []
 
    if score < 75:
 
        if not aggregate_rating:
            recommendations.append(
                "Add aggregateRating structured data (schema.org) reflecting real review scores — this is the "
                "clearest quantifiable sentiment signal available to both search and AI engines."
            )
 
        if not onpage_sentiment["has_review_or_testimonial_section"]:
            recommendations.append(
                "Add a visible customer reviews or testimonials section to help establish sentiment signals "
                "directly on your own pages, not just third-party review sites."
            )
 
        if onpage_sentiment["negative_mentions"] > onpage_sentiment["positive_mentions"]:
            recommendations.append(
                "Negative sentiment language appears more frequently than positive language on this page — "
                "review whether this reflects genuine unaddressed complaints worth resolving."
            )
 
        recommendations.append(
            "For an accurate read on aggregate web sentiment, monitor third-party review platforms (Google, "
            "Trustpilot, industry-specific review sites) and periodically query AI assistants directly about "
            "the brand (see metric 100) rather than relying solely on on-page signals."
        )
 
    return {
        "factor": "Net Sentiment Across the Web",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_net_sentiment