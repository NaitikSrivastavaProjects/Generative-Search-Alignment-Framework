import re
import json
from datetime import datetime, timezone
 
 
# headings/section labels that indicate a maintained changelog or revision log
CHANGELOG_HEADING_PATTERNS = [
    "changelog",
    "change log",
    "revision history",
    "version history",
    "update history",
    "update log",
    "what's new",
    "whats new",
    "release notes"
]
 
# phrases that describe *what* changed, as opposed to just restating a date
SUBSTANTIVE_UPDATE_PHRASES = [
    "added",
    "updated section",
    "revised",
    "corrected",
    "expanded",
    "removed outdated",
    "new data",
    "new statistics",
    "rewrote",
    "clarified",
    "fixed",
    "replaced",
    "refreshed"
]
 
DATE_PATTERN = re.compile(
    r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2})\b",
    re.IGNORECASE
)
 
 
def _get_json_ld_dates(soup):
    date_published = None
    date_modified = None
 
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            date_published = date_published or block.get("datePublished")
            date_modified = date_modified or block.get("dateModified")
 
    return date_published, date_modified
 
 
def _find_changelog_section(soup):
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if any(pattern in heading_text for pattern in CHANGELOG_HEADING_PATTERNS):
            return heading
    return None
 
 
def _extract_changelog_entries(changelog_heading):
    """Walk forward from the changelog heading and pull sibling list items / paragraphs
    until the next heading of equal-or-higher level is hit."""
    entries = []
    if changelog_heading is None:
        return entries
 
    for sibling in changelog_heading.find_all_next():
        if sibling.name in ["h1", "h2", "h3", "h4"]:
            break
        if sibling.name in ["li", "p"]:
            text = sibling.get_text(" ", strip=True)
            if text:
                entries.append(text)
 
    return entries[:30]
 
 
def _is_recent(date_str, days=30):
    if not date_str:
        return False
    try:
        parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - parsed
        return delta.days <= days
    except (ValueError, TypeError):
        return False
 
 
def analyze_substantive_updates(site_data):
 
    soup = site_data.soup
 
    date_published, date_modified = _get_json_ld_dates(soup)
    changelog_heading = _find_changelog_section(soup)
    changelog_entries = _extract_changelog_entries(changelog_heading)
 
    dated_entries = [e for e in changelog_entries if DATE_PATTERN.search(e)]
 
    substantive_entries = [
        e for e in changelog_entries
        if any(phrase in e.lower() for phrase in SUBSTANTIVE_UPDATE_PHRASES)
    ]
 
    recently_modified = _is_recent(date_modified)
    same_day_bump = (
        date_published and date_modified
        and date_published[:10] != date_modified[:10]
    )
 
    # the risky pattern: dateModified was bumped recently, but there's no
    # changelog / no substantive descriptions of what actually changed
    superficial_bump_risk = recently_modified and len(substantive_entries) == 0
 
    score = 0
 
    score += min(len(changelog_entries), 10) * 3
    score += min(len(dated_entries), 8) * 4
    score += min(len(substantive_entries), 8) * 6
 
    if date_modified and not superficial_bump_risk:
        score += 10
 
    if superficial_bump_risk:
        score -= 20
 
    score = max(0, min(score, 100))
 
    details = {
        "date_published": date_published,
        "date_modified": date_modified,
        "changelog_section_found": changelog_heading is not None,
        "changelog_entries": len(changelog_entries),
        "dated_entries": len(dated_entries),
        "substantive_update_descriptions": len(substantive_entries),
        "recently_modified": recently_modified,
        "superficial_bump_risk": superficial_bump_risk
    }
 
    recommendations = []
 
    if score < 75:
 
        if changelog_heading is None:
            recommendations.append(
                "Add a visible changelog or \"What's New\" section documenting what actually changed on each update, "
                "not just when it changed."
            )
 
        if changelog_entries and len(substantive_entries) == 0:
            recommendations.append(
                "Describe the substance of each update (e.g. \"added new data\", \"corrected outdated figures\") "
                "rather than only listing dates — LLMs can detect superficial date-only changes."
            )
 
        if superficial_bump_risk:
            recommendations.append(
                "dateModified was updated recently but no substantive change is documented on the page — "
                "this pattern is a signal of a superficial date bump rather than a real content refresh."
            )
 
        if len(dated_entries) < 2:
            recommendations.append(
                "Keep a running, dated log of edits so recency signals are backed by verifiable update history."
            )
 
    return {
        "factor": "Substantive Updates (Not Just Date Bumps)",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_substantive_updates