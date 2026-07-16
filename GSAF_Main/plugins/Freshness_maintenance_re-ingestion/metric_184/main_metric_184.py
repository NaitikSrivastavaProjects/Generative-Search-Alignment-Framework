import re
from datetime import datetime
 
 
# a "statistic" = a number followed by a unit/qualifier that reads like data,
# not just any digit on the page
STAT_PATTERN = re.compile(
    r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(%|percent|million|billion|thousand|"
    r"respondents|participants|users|customers|companies)\b",
    re.IGNORECASE
)
 
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
 
# phrases that typically precede/follow a cited source for a statistic
SOURCE_ATTRIBUTION_PHRASES = [
    "according to",
    "source:",
    "data from",
    "study by",
    "survey by",
    "report by",
    "research from",
    "as of",
    "per a",
    "based on data"
]
 
WINDOW = 80  # characters of context to scan around each stat for a nearby year/source
 
 
def _find_stats_with_context(text):
    """Return list of (stat_match_text, surrounding_context) tuples."""
    results = []
    for match in STAT_PATTERN.finditer(text):
        start = max(0, match.start() - WINDOW)
        end = min(len(text), match.end() + WINDOW)
        context = text[start:end]
        results.append((match.group(0), context))
    return results
 
 
def analyze_statistic_refresh_cadence(site_data):
 
    soup = site_data.soup
    text = soup.get_text(" ", strip=True)
    lower_text = text.lower()
    current_year = datetime.now().year
 
    stats_with_context = _find_stats_with_context(text)
    total_stats = len(stats_with_context)
 
    stats_with_year_nearby = 0
    stats_with_current_or_recent_year = 0
    stats_with_stale_year = 0
    stats_with_source_attribution = 0
 
    for stat_text, context in stats_with_context:
        years_in_context = [int(y) for y in YEAR_PATTERN.findall(context)]
        context_lower = context.lower()
 
        if years_in_context:
            stats_with_year_nearby += 1
            most_recent_nearby_year = max(years_in_context)
            if most_recent_nearby_year >= current_year - 1:
                stats_with_current_or_recent_year += 1
            elif most_recent_nearby_year < current_year - 2:
                stats_with_stale_year += 1
 
        if any(phrase in context_lower for phrase in SOURCE_ATTRIBUTION_PHRASES):
            stats_with_source_attribution += 1
 
    pct_with_year = (stats_with_year_nearby / total_stats * 100) if total_stats else 0
    pct_recent = (stats_with_current_or_recent_year / total_stats * 100) if total_stats else 0
    pct_sourced = (stats_with_source_attribution / total_stats * 100) if total_stats else 0
 
    score = 0
 
    if total_stats > 0:
        score += min(total_stats, 10) * 3
        score += round(pct_recent * 0.4)
        score += round(pct_sourced * 0.3)
 
        if stats_with_stale_year > 0 and stats_with_current_or_recent_year == 0:
            score -= 20
 
    score = max(0, min(score, 100))
 
    details = {
        "total_statistics_found": total_stats,
        "statistics_with_year_nearby": stats_with_year_nearby,
        "statistics_with_recent_year": stats_with_current_or_recent_year,
        "statistics_with_stale_year": stats_with_stale_year,
        "statistics_with_source_attribution": stats_with_source_attribution,
        "pct_recent": round(pct_recent, 1),
        "pct_sourced": round(pct_sourced, 1),
        "current_year_checked": current_year
    }
 
    recommendations = []
 
    if score < 75:
 
        if total_stats == 0:
            recommendations.append(
                "Add concrete statistics with sourced data — pages with no numbers have nothing to refresh or age-check."
            )
 
        if total_stats > 0 and stats_with_year_nearby == 0:
            recommendations.append(
                "Attach a year to each statistic (e.g. \"32% of users in 2026\") so freshness can be verified at a glance."
            )
 
        if stats_with_stale_year > 0:
            recommendations.append(
                f"{stats_with_stale_year} statistic(s) reference data older than {current_year - 2} — "
                f"refresh these with sources from {current_year - 1} or {current_year}."
            )
 
        if total_stats > 0 and stats_with_source_attribution < total_stats:
            recommendations.append(
                "Cite a source (e.g. \"according to...\", \"source:\") next to each statistic so updates can be "
                "traced back to a verifiable, dated origin."
            )
 
    return {
        "factor": "Statistic Refresh Cadence",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_statistic_refresh_cadence