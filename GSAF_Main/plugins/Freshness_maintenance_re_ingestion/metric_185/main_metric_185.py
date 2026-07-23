import re
 
 
# phrases that indicate the page itself acknowledges it may be obsolete/outdated
OBSOLETE_ACKNOWLEDGMENT_PHRASES = [
    "no longer accurate",
    "no longer applicable",
    "no longer maintained",
    "no longer supported",
    "this page is outdated",
    "this article is outdated",
    "this information may be outdated",
    "content may be out of date",
    "deprecated",
    "this feature has been discontinued",
    "this product is discontinued",
    "archived page",
    "this page has been archived"
]
 
# phrases that indicate a *proper* forward-pointing resolution exists on the page
# (as opposed to just a bare disclaimer with nothing actionable)
FORWARD_POINTER_PHRASES = [
    "has moved to",
    "please visit",
    "see the updated",
    "see our current",
    "redirecting to",
    "click here for the latest",
    "for current information, see",
    "this page has been replaced by",
    "updated version available"
]
 
 
def _get_meta_robots(soup):
    tag = soup.find("meta", attrs={"name": "robots"})
    return tag["content"].lower() if tag and tag.get("content") else ""
 
 
def _get_canonical_url(soup):
    tag = soup.find("link", attrs={"rel": "canonical"})
    return tag["href"] if tag and tag.get("href") else None
 
 
def analyze_deprecated_page_handling(site_data):
 
    soup = site_data.soup
    text = soup.get_text(" ", strip=True)
    lower_text = text.lower()
 
    # these depend on what the crawler in utils/helpers.py attaches to site_data;
    # fall back gracefully if not present so this plugin never hard-crashes the batch
    status_code = getattr(site_data, "status_code", None)
    was_redirected = getattr(site_data, "was_redirected", None)
    final_url = getattr(site_data, "final_url", None)
    requested_url = getattr(site_data, "url", None)
 
    if was_redirected is None and final_url and requested_url:
        was_redirected = final_url != requested_url
 
    is_redirect_status = isinstance(status_code, int) and 300 <= status_code < 400
 
    meta_robots = _get_meta_robots(soup)
    is_noindexed = "noindex" in meta_robots
 
    canonical_url = _get_canonical_url(soup)
    canonical_points_elsewhere = bool(
        canonical_url and requested_url and canonical_url.rstrip("/") != requested_url.rstrip("/")
    )
 
    acknowledges_obsolescence = any(
        phrase in lower_text for phrase in OBSOLETE_ACKNOWLEDGMENT_PHRASES
    )
    has_forward_pointer = any(
        phrase in lower_text for phrase in FORWARD_POINTER_PHRASES
    )
 
    # the failure mode this metric targets: the page admits it's outdated/deprecated
    # but is still live, indexable, with no redirect, no canonical elsewhere, and no
    # forward pointer to current info -- i.e. dead info left live with no resolution
    properly_handled = (
        is_redirect_status
        or was_redirected
        or is_noindexed
        or canonical_points_elsewhere
        or (acknowledges_obsolescence and has_forward_pointer)
    )
 
    improperly_left_live = acknowledges_obsolescence and not properly_handled
 
    score = 0
 
    if is_redirect_status or was_redirected:
        score = 100
    elif is_noindexed or canonical_points_elsewhere:
        score = 90
    elif acknowledges_obsolescence and has_forward_pointer:
        score = 80
    elif acknowledges_obsolescence and not has_forward_pointer:
        score = 15
    else:
        # no evidence either way this page is obsolete -- treat as not applicable
        # to this specific check, but not penalized since we can't confirm staleness
        score = 70
 
    details = {
        "status_code": status_code,
        "was_redirected": bool(was_redirected),
        "is_noindexed": is_noindexed,
        "canonical_url": canonical_url,
        "canonical_points_elsewhere": canonical_points_elsewhere,
        "acknowledges_obsolescence_on_page": acknowledges_obsolescence,
        "has_forward_pointer_to_current_info": has_forward_pointer,
        "improperly_left_live": improperly_left_live
    }
 
    recommendations = []
 
    if score < 75:
 
        if improperly_left_live:
            recommendations.append(
                "This page acknowledges it's outdated/deprecated but has no redirect, canonical, noindex, or "
                "forward pointer to current content — either 301 redirect to the updated page, rewrite the "
                "content in place, or add a clear link to its replacement."
            )
 
        if acknowledges_obsolescence and not has_forward_pointer:
            recommendations.append(
                "Add a direct link to the current/replacement page rather than leaving the disclaimer without "
                "a next step for the reader (or the crawling LLM)."
            )
 
        if not is_redirect_status and not was_redirected and not is_noindexed and not canonical_points_elsewhere and not acknowledges_obsolescence:
            recommendations.append(
                "If this page's content is no longer accurate or relevant, redirect it to an updated resource "
                "or rewrite it in place rather than leaving stale information live and indexable."
            )
 
    return {
        "factor": "Deprecate Obsolete Pages Properly",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_deprecated_page_handling