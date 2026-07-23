import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
 
 
FEED_LINK_TYPES = [
    "application/rss+xml",
    "application/atom+xml",
    "application/feed+json",
    "application/json"
]
 
# common guessable feed paths to fall back on if no <link rel="alternate"> is declared
FALLBACK_FEED_PATHS = ["/feed", "/feed/", "/rss", "/rss.xml", "/atom.xml", "/feed.xml"]
 
FEED_FETCH_TIMEOUT = 8
 
 
def _find_declared_feed_urls(soup):
    feeds = []
    for link in soup.find_all("link", attrs={"rel": "alternate"}):
        link_type = (link.get("type") or "").lower()
        href = link.get("href")
        if href and any(t in link_type for t in FEED_LINK_TYPES):
            feeds.append(href)
    return feeds
 
 
def _guess_fallback_feed_urls(base_url):
    if not base_url:
        return []
    base_url = base_url.rstrip("/")
    return [base_url + path for path in FALLBACK_FEED_PATHS]
 
 
def _parse_pubdate(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
 
 
def _inspect_feed(feed_url):
    """Fetch and parse a feed URL. Returns dict with reachability/freshness info,
    or None if it couldn't be fetched/parsed as a feed at all."""
    try:
        response = requests.get(feed_url, timeout=FEED_FETCH_TIMEOUT)
        if response.status_code != 200:
            return None
 
        root = ET.fromstring(response.content)
    except (requests.RequestException, ET.ParseError):
        return None
 
    # RSS 2.0: rss/channel/item ; Atom: feed/entry (namespaced)
    items = root.findall(".//item")
    pub_dates = [
        _parse_pubdate(item.findtext("pubDate"))
        for item in items
        if item.findtext("pubDate")
    ]
 
    if not items:
        # try Atom namespace-agnostic entry lookup
        entries = [el for el in root.iter() if el.tag.endswith("entry")]
        items = entries
        for entry in entries:
            updated = None
            for child in entry:
                if child.tag.endswith("updated") or child.tag.endswith("published"):
                    updated = _parse_pubdate(child.text)
                    if updated:
                        pub_dates.append(updated)
                        break
 
    pub_dates = [d for d in pub_dates if d is not None]
    most_recent = max(pub_dates) if pub_dates else None
 
    return {
        "reachable": True,
        "item_count": len(items),
        "most_recent_item_date": most_recent.isoformat() if most_recent else None,
        "most_recent_item_dt": most_recent
    }
 
 
def analyze_rss_feed_maintenance(site_data):
 
    soup = site_data.soup
    base_url = getattr(site_data, "url", None) or getattr(site_data, "final_url", None)
 
    declared_feeds = _find_declared_feed_urls(soup)
    feed_candidates = declared_feeds if declared_feeds else _guess_fallback_feed_urls(base_url)
 
    feed_result = None
    working_feed_url = None
 
    for feed_url in feed_candidates:
        result = _inspect_feed(feed_url)
        if result:
            feed_result = result
            working_feed_url = feed_url
            break
 
    feed_declared = len(declared_feeds) > 0
    feed_reachable = feed_result is not None
 
    days_since_last_item = None
    is_actively_updated = False
 
    if feed_reachable and feed_result.get("most_recent_item_dt"):
        most_recent_dt = feed_result["most_recent_item_dt"]
        if most_recent_dt.tzinfo is None:
            most_recent_dt = most_recent_dt.replace(tzinfo=timezone.utc)
        days_since_last_item = (datetime.now(timezone.utc) - most_recent_dt).days
        is_actively_updated = days_since_last_item <= 90
 
    score = 0
 
    if feed_declared:
        score += 25
    elif feed_reachable:
        # feed exists at a guessable path but isn't declared in <head> --
        # discoverable by humans/scrapers guessing, but not properly linked
        score += 10
 
    if feed_reachable:
        score += 25
        score += min(feed_result.get("item_count", 0), 10) * 3
 
        if is_actively_updated:
            score += 20
        elif days_since_last_item is not None and days_since_last_item > 180:
            score -= 15
 
    score = max(0, min(score, 100))
 
    details = {
        "feed_declared_in_head": feed_declared,
        "declared_feed_urls": declared_feeds,
        "feed_reachable": feed_reachable,
        "working_feed_url": working_feed_url,
        "feed_item_count": feed_result.get("item_count") if feed_result else 0,
        "most_recent_item_date": feed_result.get("most_recent_item_date") if feed_result else None,
        "days_since_last_item": days_since_last_item,
        "actively_updated": is_actively_updated
    }
 
    recommendations = []
 
    if score < 75:
 
        if not feed_declared and not feed_reachable:
            recommendations.append(
                "Publish an RSS or Atom feed and declare it with a <link rel=\"alternate\" type=\"application/rss+xml\"> "
                "tag in the page <head> — some retrieval pipelines rely on feeds to discover and re-ingest content."
            )
 
        if feed_reachable and not feed_declared:
            recommendations.append(
                "An RSS feed appears to exist but isn't declared in the page <head> — add the <link rel=\"alternate\"> "
                "tag so it's reliably discoverable rather than guessed at a conventional path."
            )
 
        if feed_reachable and feed_result.get("item_count", 0) == 0:
            recommendations.append(
                "The feed is reachable but contains no items — populate it with recent content."
            )
 
        if feed_reachable and days_since_last_item is not None and days_since_last_item > 90:
            recommendations.append(
                f"The feed's most recent item is {days_since_last_item} days old — keep it updated with new "
                "or revised content to signal an actively maintained source."
            )
 
    return {
        "factor": "RSS Feeds Maintained",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_rss_feed_maintenance