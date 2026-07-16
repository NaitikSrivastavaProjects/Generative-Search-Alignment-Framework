import re
from datetime import datetime
 
 
# superlative / freshness-signaling words that pair with a year in a title
# to signal "this is the current-year definitive version" (e.g. "Best X in 2026")
SUPERLATIVE_PATTERNS = [
    "best",
    "top",
    "guide",
    "review",
    "comparison",
    "ranked",
    "checklist",
    "trends",
    "updated"
]
 
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
 
 
def _extract_titles(soup):
    title_tag = soup.find("title")
    h1_tag = soup.find("h1")
    meta_title = soup.find("meta", attrs={"property": "og:title"})
 
    return {
        "title": title_tag.get_text(strip=True) if title_tag else "",
        "h1": h1_tag.get_text(strip=True) if h1_tag else "",
        "og_title": meta_title["content"] if meta_title and meta_title.get("content") else ""
    }
 
 
def analyze_year_in_title(site_data):
 
    soup = site_data.soup
    current_year = datetime.now().year
 
    titles = _extract_titles(soup)
    combined_text = " ".join(titles.values())
    lower_text = combined_text.lower()
 
    years_found = [int(y) for y in YEAR_PATTERN.findall(combined_text)]
 
    has_current_year = current_year in years_found
    has_next_year = (current_year + 1) in years_found
    has_outdated_year = any(y < current_year for y in years_found)
 
    has_superlative = any(word in lower_text for word in SUPERLATIVE_PATTERNS)
 
    # "surfaces in current-year queries" requires BOTH a superlative/list-style
    # framing AND a current (or next) year explicitly in the title/H1
    strong_signal = has_superlative and (has_current_year or has_next_year)
 
    score = 0
 
    if has_current_year:
        score += 50
    elif has_next_year:
        score += 40
    elif has_outdated_year:
        score += 10
    else:
        score += 0
 
    if has_superlative:
        score += 20
 
    if strong_signal:
        score += 30
 
    score = min(score, 100)
 
    details = {
        "title": titles["title"],
        "h1": titles["h1"],
        "years_found": years_found,
        "has_current_year": has_current_year,
        "has_next_year": has_next_year,
        "has_outdated_year": has_outdated_year,
        "has_superlative_framing": has_superlative,
        "current_year_checked": current_year
    }
 
    recommendations = []
 
    if score < 75:
 
        if not years_found:
            recommendations.append(
                f"Include the current year ({current_year}) in the title or H1, e.g. \"Best X in {current_year}\", "
                "so the page surfaces in current-year queries."
            )
        elif has_outdated_year and not (has_current_year or has_next_year):
            recommendations.append(
                f"Update the year in the title/H1 from {min(y for y in years_found if y < current_year)} "
                f"to {current_year} to avoid appearing stale in current-year queries."
            )
 
        if not has_superlative:
            recommendations.append(
                "Pair the year with a superlative or list-style framing (e.g. \"Best\", \"Top\", \"Guide\") "
                "to strengthen relevance for current-year comparison queries."
            )
 
    return {
        "factor": "Year in Title",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_year_in_title
 