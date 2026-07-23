import os
import re
import json
import requests
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
 
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")
 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
 
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
 
REQUEST_TIMEOUT = 30
 
 
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
 
 
def _build_query(brand_name, keyword):
    if keyword:
        return f"What are the best options for {keyword}? Please name specific companies or products."
    return f"What can you tell me about \"{brand_name}\" and what they do?"
 
 
def _mentions_brand(response_text, brand_name, domain):
    if not response_text:
        return False
    lower = response_text.lower()
    if brand_name and brand_name.lower() in lower:
        return True
    if domain and domain.lower() in lower:
        return True
    return False
 
 
def _query_gemini(query):
    if not GEMINI_API_KEY:
        return None
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": query}]}]},
            timeout=REQUEST_TIMEOUT
        )
        raw = response.json()
        return raw["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini monitoring query error: {e}")
        return None
 
 
def _query_openai(query):
    if not OPENAI_API_KEY:
        return None
    try:
        response = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": query}]
            },
            timeout=REQUEST_TIMEOUT
        )
        raw = response.json()
        return raw["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI monitoring query error: {e}")
        return None
 
 
def _query_anthropic(query):
    if not ANTHROPIC_API_KEY:
        return None
    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": query}]
            },
            timeout=REQUEST_TIMEOUT
        )
        raw = response.json()
        text_blocks = [b["text"] for b in raw.get("content", []) if b.get("type") == "text"]
        return " ".join(text_blocks)
    except Exception as e:
        print(f"Anthropic monitoring query error: {e}")
        return None
 
 
def _query_perplexity(query):
    if not PERPLEXITY_API_KEY:
        return None
    try:
        response = requests.post(
            PERPLEXITY_URL,
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": query}]
            },
            timeout=REQUEST_TIMEOUT
        )
        raw = response.json()
        return raw["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Perplexity monitoring query error: {e}")
        return None
 
 
def analyze_direct_ai_answer_monitoring(site_data):
 
    soup = site_data.soup
    brand_name = _extract_brand_name(soup)
 
    site_url = getattr(site_data, "url", None) or getattr(site_data, "final_url", None)
    domain = urlparse(site_url).netloc.replace("www.", "") if site_url else None
 
    keyword = getattr(site_data, "keyword", None) or ""
    keywords = getattr(site_data, "keywords", None) or []
    primary_keyword = keyword or (keywords[0] if keywords else None)
 
    query = _build_query(brand_name, primary_keyword)
 
    providers = {
        "gemini": (_query_gemini, GEMINI_API_KEY),
        "openai_chatgpt": (_query_openai, OPENAI_API_KEY),
        "anthropic_claude": (_query_anthropic, ANTHROPIC_API_KEY),
        "perplexity": (_query_perplexity, PERPLEXITY_API_KEY),
    }
 
    results = {}
    configured_providers = 0
    responsive_providers = 0
    citing_providers = 0
 
    for name, (query_fn, api_key) in providers.items():
        if not api_key:
            results[name] = {"configured": False, "queried": False, "brand_mentioned": None}
            continue
 
        configured_providers += 1
        response_text = query_fn(query)
 
        if response_text is None:
            results[name] = {"configured": True, "queried": False, "brand_mentioned": None}
            continue
 
        responsive_providers += 1
        mentioned = _mentions_brand(response_text, brand_name, domain)
        if mentioned:
            citing_providers += 1
 
        results[name] = {
            "configured": True,
            "queried": True,
            "brand_mentioned": mentioned,
            "response_excerpt": response_text[:300]
        }
 
    if configured_providers == 0:
        score = 50  # no provider API keys configured -- cannot run monitoring at all
    elif responsive_providers == 0:
        score = 50  # configured but all requests failed (network/auth issues)
    else:
        score = round((citing_providers / responsive_providers) * 100)
 
    score = max(0, min(score, 100))
 
    details = {
        "brand_name_detected": brand_name,
        "domain_checked": domain,
        "query_used": query,
        "providers_configured": configured_providers,
        "providers_responsive": responsive_providers,
        "providers_citing_brand": citing_providers,
        "provider_results": results,
        "note": (
            "This metric is inherently a recurring monitoring process, not a one-time page check. Run this "
            "on a schedule (e.g. weekly) across multiple brand + keyword queries and track citation trends "
            "over time -- a single run is only a snapshot."
        )
    }
 
    recommendations = []
 
    if configured_providers == 0:
        recommendations.append(
            "No AI provider API keys are configured (GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, "
            "PERPLEXITY_API_KEY) -- add at least one to enable direct AI answer monitoring."
        )
    elif responsive_providers < configured_providers:
        recommendations.append(
            "One or more configured AI providers failed to respond -- check API keys and rate limits."
        )
 
    if configured_providers > 0 and responsive_providers > 0 and citing_providers < responsive_providers:
        recommendations.append(
            f"The brand was cited by {citing_providers} of {responsive_providers} queried AI assistants for "
            f"this query. Strengthen entity signals (schema, citations, press coverage, case studies) to "
            "improve citation rate across all major AI answer engines."
        )
 
    recommendations.append(
        "Set this metric up to run on a recurring schedule with a broader set of brand + key-term queries, "
        "and track citation rate over time rather than relying on a single snapshot."
    )
 
    return {
        "factor": "Direct AI Answer Monitoring",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_direct_ai_answer_monitoring