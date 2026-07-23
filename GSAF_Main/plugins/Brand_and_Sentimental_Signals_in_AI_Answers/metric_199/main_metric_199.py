import re
import json
from datetime import datetime, timezone
 
 
CASE_STUDY_INDEX_HEADING_PATTERNS = [
    "case studies", "customer stories", "success stories", "client stories",
    "customer spotlight", "success spotlight", "who uses", "customers"
]
 
CASE_STUDY_LINK_PATH_HINTS = [
    "case-stud", "casestud", "customer-stor", "success-stor",
    "client-stor", "customer-spotlight"
]
 
DATE_PATTERN = re.compile(
    r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b|"
    r"\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?)\s+(\d{1,2})?,?\s*(20\d{2})\b",
    re.IGNORECASE
)
 
MIN_STORIES_FOR_ACTIVE_PROGRAM = 3
RECENT_WINDOW_DAYS = 180
 
 
def _find_case_study_index_section(soup):
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if any(pattern in heading_text for pattern in CASE_STUDY_INDEX_HEADING_PATTERNS):
            return heading
    return None
 
 
def _find_case_study_links(soup):
    links = soup.find_all("a", href=True)
    case_study_links = []
    for link in links:
        href = link["href"].lower()
        if any(hint in href for hint in CASE_STUDY_LINK_PATH_HINTS):
            case_study_links.append(link)
    return case_study_links
 
 
def _extract_nearby_date(link_tag):
    """Look at the link's own text, its parent card, and a couple of siblings
    for a parseable date -- publish dates on story cards are often in a
    sibling <span>/<time> element rather than inside the <a> itself."""
    candidates_text = [link_tag.get_text(" ", strip=True)]
 
    parent = link_tag.find_parent(["article", "div", "li"])
    if parent:
        time_tag = parent.find("time")
        if time_tag:
            candidates_text.append(time_tag.get("datetime", "") or time_tag.get_text(strip=True))
        candidates_text.append(parent.get_text(" ", strip=True)[:200])
 
    for text in candidates_text:
        match = DATE_PATTERN.search(text)
        if match:
            return match.group(0)
 
    return None
 
 
def _parse_date_string(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None
 
 
def _get_json_ld_article_dates(soup):
    dates = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if isinstance(block, dict) and block.get("@type") in ("Article", "CaseStudy", "CreativeWork"):
                if block.get("datePublished"):
                    dates.append(block["datePublished"])
    return dates
 
 
def analyze_active_customer_story_publishing(site_data):
 
    soup = site_data.soup
 
    index_section = _find_case_study_index_section(soup)
    case_study_links = _find_case_study_links(soup)
 
    unique_hrefs = list({link["href"] for link in case_study_links})
    total_stories_found = len(unique_hrefs)
 
    dated_stories = []
    for link in case_study_links:
        date_str = _extract_nearby_date(link)
        parsed = _parse_date_string(date_str)
        if parsed:
            dated_stories.append(parsed)
 
    schema_dates_raw = _get_json_ld_article_dates(soup)
    for raw_date in schema_dates_raw:
        parsed = _parse_date_string(raw_date)
        if parsed:
            dated_stories.append(parsed)
 
    now = datetime.now(timezone.utc)
    dated_stories.sort(reverse=True)
    most_recent_story_date = dated_stories[0] if dated_stories else None
    days_since_most_recent = (now - most_recent_story_date).days if most_recent_story_date else None
 
    stories_within_recent_window = sum(
        1 for d in dated_stories if (now - d).days <= RECENT_WINDOW_DAYS
    )
 
    has_active_program = total_stories_found >= MIN_STORIES_FOR_ACTIVE_PROGRAM
    is_recently_active = days_since_most_recent is not None and days_since_most_recent <= RECENT_WINDOW_DAYS
 
    score = 0
 
    if total_stories_found > 0:
        score += 20
        score += min(total_stories_found, 15) * 3
 
        if index_section is not None:
            score += 10
 
        if dated_stories:
            score += min(stories_within_recent_window, 5) * 4
            if is_recently_active:
                score += 10
            elif days_since_most_recent is not None and days_since_most_recent > 365:
                score -= 15
    else:
        score = 0
 
    score = max(0, min(score, 100))
 
    details = {
        "case_study_index_section_found": index_section is not None,
        "total_customer_stories_found": total_stories_found,
        "stories_with_identifiable_date": len(dated_stories),
        "most_recent_story_date": most_recent_story_date.isoformat() if most_recent_story_date else None,
        "days_since_most_recent_story": days_since_most_recent,
        "stories_published_within_last_180_days": stories_within_recent_window,
        "has_active_publishing_program": has_active_program,
        "is_recently_active": is_recently_active
    }
 
    recommendations = []
 
    if score < 75:
 
        if total_stories_found == 0:
            recommendations.append(
                "Publish customer stories or case studies — these directly feed \"who uses X\" and similar "
                "comparison queries in AI-generated answers."
            )
        elif not has_active_program:
            recommendations.append(
                f"Only {total_stories_found} customer stor{'y' if total_stories_found == 1 else 'ies'} found — "
                f"build toward at least {MIN_STORIES_FOR_ACTIVE_PROGRAM} to establish a credible, ongoing program "
                "rather than a one-off case study."
            )
 
        if total_stories_found > 0 and index_section is None:
            recommendations.append(
                "Add a dedicated \"Customer Stories\" or \"Case Studies\" index page/section so stories are "
                "discoverable as a collection, not scattered individual pages."
            )
 
        if dated_stories and days_since_most_recent is not None and days_since_most_recent > RECENT_WINDOW_DAYS:
            recommendations.append(
                f"The most recent customer story is {days_since_most_recent} days old — publish new stories "
                "regularly to signal an active program rather than a stale, one-time effort."
            )
 
        if total_stories_found > 0 and len(dated_stories) < total_stories_found:
            recommendations.append(
                "Add visible publish dates to customer stories (e.g. via a <time> element or datePublished schema) "
                "so publishing cadence can be verified."
            )
 
    return {
        "factor": "Active Customer Story Publishing",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_active_customer_story_publishing