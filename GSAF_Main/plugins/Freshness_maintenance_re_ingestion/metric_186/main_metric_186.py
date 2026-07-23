import re
from datetime import datetime, timezone
 
 
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
 
# indicates a formal version numbering scheme (v1.2, version 3, 2.0.1, etc.)
VERSION_NUMBER_PATTERN = re.compile(
    r"\b(?:v(?:ersion)?\.?\s?\d+(?:\.\d+){0,2})\b",
    re.IGNORECASE
)
 
DATE_PATTERN = re.compile(
    r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b|"
    r"\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?)\s+(\d{1,2}),?\s+(20\d{2})\b",
    re.IGNORECASE
)
 
 
def _find_changelog_section(soup):
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if any(pattern in heading_text for pattern in CHANGELOG_HEADING_PATTERNS):
            return heading
    return None
 
 
def _extract_entries(changelog_heading):
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
 
    return entries[:50]
 
 
def _parse_most_recent_year(entries):
    years = []
    for entry in entries:
        for match in re.finditer(r"\b(20\d{2})\b", entry):
            years.append(int(match.group(1)))
    return max(years) if years else None
 
 
def analyze_changelog_version_history(site_data):
 
    soup = site_data.soup
    current_year = datetime.now(timezone.utc).year
 
    changelog_heading = _find_changelog_section(soup)
    entries = _extract_entries(changelog_heading)
 
    dated_entries = [e for e in entries if DATE_PATTERN.search(e)]
    versioned_entries = [e for e in entries if VERSION_NUMBER_PATTERN.search(e)]
 
    most_recent_year = _parse_most_recent_year(entries)
    is_actively_maintained = most_recent_year is not None and most_recent_year >= current_year - 1
 
    has_changelog = changelog_heading is not None
    has_multiple_entries = len(entries) >= 3
 
    score = 0
 
    if has_changelog:
        score += 30
        score += min(len(entries), 10) * 3
        score += min(len(dated_entries), 8) * 3
        score += min(len(versioned_entries), 5) * 2
 
        if is_actively_maintained:
            score += 15
        elif most_recent_year is not None and most_recent_year < current_year - 2:
            score -= 15
 
    score = max(0, min(score, 100))
 
    details = {
        "changelog_section_found": has_changelog,
        "total_entries": len(entries),
        "dated_entries": len(dated_entries),
        "versioned_entries": len(versioned_entries),
        "most_recent_entry_year": most_recent_year,
        "actively_maintained": is_actively_maintained,
        "current_year_checked": current_year
    }
 
    recommendations = []
 
    if score < 75:
 
        if not has_changelog:
            recommendations.append(
                "Add a changelog or version history section (e.g. \"What's New\", \"Update History\") on evergreen "
                "pages to demonstrate active, ongoing maintenance."
            )
 
        if has_changelog and not has_multiple_entries:
            recommendations.append(
                "Build out the changelog with more than one or two entries — a single entry reads as a one-time "
                "edit rather than active maintenance."
            )
 
        if has_changelog and len(dated_entries) < len(entries):
            recommendations.append(
                "Timestamp every changelog entry — undated entries can't be used as freshness/maintenance signals."
            )
 
        if has_changelog and most_recent_year is not None and most_recent_year < current_year - 1:
            recommendations.append(
                f"The most recent changelog entry is from {most_recent_year} — add a current-year entry "
                "or the page will read as unmaintained despite having a changelog."
            )
 
        if has_changelog and len(versioned_entries) == 0:
            recommendations.append(
                "Consider formal version numbering (e.g. v1.2, v2.0) alongside dates for clearer, more "
                "citable maintenance history."
            )
 
    return {
        "factor": "Changelog / Version History on Evergreen Pages",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_changelog_version_history
