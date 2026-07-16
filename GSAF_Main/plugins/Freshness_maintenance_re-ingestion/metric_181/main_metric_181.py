import re
import json
 
 
# phrases that signal the page/site has been featured in outside press
PRESS_MENTION_PHRASES = [
    "as featured in",
    "as seen on",
    "as seen in",
    "featured on",
    "featured in",
    "in the press",
    "in the news",
    "media coverage",
    "press coverage",
    "press mentions",
    "as reported by",
    "as covered by"
]
 
# phrases that tie press coverage specifically to an *update* or *re-launch*
# (this is what separates metric 88 from a generic "as seen on" badge wall)
UPDATE_LINKED_PHRASES = [
    "announced today",
    "announces",
    "newly updated",
    "just updated",
    "latest update",
    "recently updated",
    "new release",
    "relaunch",
    "re-launch",
    "press release",
    "official announcement"
]
 
# known news / media domains worth crediting when linked out to
NEWS_DOMAINS = [
    "techcrunch.com", "forbes.com", "businessinsider.com", "reuters.com",
    "apnews.com", "bloomberg.com", "cnbc.com", "nytimes.com", "wsj.com",
    "theverge.com", "wired.com", "venturebeat.com", "prnewswire.com",
    "businesswire.com", "globenewswire.com", "axios.com", "bbc.com"
]
 
# schema.org types that indicate a formal press/news artifact
PRESS_SCHEMA_TYPES = ["NewsArticle", "PressRelease", "Report"]
 
 
def _get_json_ld_types(soup):
    types_found = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            t = block.get("@type", "")
            if isinstance(t, list):
                types_found.extend(t)
            elif t:
                types_found.append(t)
    return types_found
 
 
def analyze_press_coverage_updates(site_data):
 
    soup = site_data.soup
    text = soup.get_text(" ", strip=True)
    lower_text = text.lower()
 
    press_mentions = 0
    for phrase in PRESS_MENTION_PHRASES:
        press_mentions += lower_text.count(phrase)
 
    update_linked_mentions = 0
    for phrase in UPDATE_LINKED_PHRASES:
        update_linked_mentions += lower_text.count(phrase)
 
    outbound_links = [
        a["href"] for a in soup.find_all("a", href=True)
        if a["href"].startswith("http")
    ]
    news_domain_links = [
        link for link in outbound_links
        if any(domain in link for domain in NEWS_DOMAINS)
    ]
 
    schema_types = _get_json_ld_types(soup)
    press_schema_present = any(t in PRESS_SCHEMA_TYPES for t in schema_types)
 
    score = 0
 
    score += min(press_mentions, 5) * 8
    score += min(update_linked_mentions, 5) * 8
    score += min(len(set(news_domain_links)), 6) * 6
    score += 20 if press_schema_present else 0
 
    score = min(score, 100)
 
    details = {
        "press_mention_phrases": press_mentions,
        "update_linked_phrases": update_linked_mentions,
        "news_domain_links": len(set(news_domain_links)),
        "news_domains_linked": sorted(set(
            domain for link in news_domain_links
            for domain in NEWS_DOMAINS if domain in link
        )),
        "press_schema_present": press_schema_present
    }
 
    recommendations = []
 
    if score < 75:
 
        if press_mentions == 0:
            recommendations.append(
                "Reference press coverage directly on the page (e.g. \"as featured in\", \"as seen on\")."
            )
 
        if update_linked_mentions == 0:
            recommendations.append(
                "Tie announcements or press releases to specific product/content updates so re-crawls and "
                "re-ingestion by LLMs get triggered by fresh external mentions."
            )
 
        if len(news_domain_links) == 0:
            recommendations.append(
                "Link out to or reference reputable news/media outlets that have covered your updates."
            )
 
        if not press_schema_present:
            recommendations.append(
                "Add NewsArticle or PressRelease structured data (schema.org) for any press coverage referenced on the page."
            )
 
    return {
        "factor": "Press Coverage of Updates",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_press_coverage_updates
 