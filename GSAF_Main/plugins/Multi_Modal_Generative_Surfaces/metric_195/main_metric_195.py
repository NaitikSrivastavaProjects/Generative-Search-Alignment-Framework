import re
import json
 
 
CC_LICENSE_DOMAINS = [
    "creativecommons.org",
    "creativecommons.org/licenses",
    "creativecommons.org/publicdomain"
]
 
CC_LICENSE_TEXT_PATTERNS = [
    r"\bcc\s?by\b", r"\bcc\s?by-sa\b", r"\bcc\s?by-nc\b", r"\bcc\s?by-nd\b",
    r"\bcc\s?by-nc-sa\b", r"\bcc\s?by-nc-nd\b", r"\bcc0\b",
    r"\bcreative commons\b", r"\bpublic domain\b"
]
 
ALL_RIGHTS_RESERVED_PATTERNS = [
    r"\ball rights reserved\b",
    r"\bcopyright\b.{0,5}\d{4}\b"
]
 
 
def _extract_json_ld_image_licenses(soup):
    licensed_image_urls = []
 
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            candidates = [block] + (block.get("@graph") if isinstance(block.get("@graph"), list) else [])
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                if candidate.get("@type") == "ImageObject" and candidate.get("license"):
                    license_value = candidate["license"]
                    is_cc = isinstance(license_value, str) and any(
                        domain in license_value.lower() for domain in CC_LICENSE_DOMAINS
                    )
                    licensed_image_urls.append({
                        "url": candidate.get("contentUrl") or candidate.get("url"),
                        "license": license_value,
                        "is_creative_commons": is_cc
                    })
 
    return licensed_image_urls
 
 
def _find_rel_license_links(soup):
    return [a for a in soup.find_all("a", attrs={"rel": True}) if "license" in a.get("rel", [])]
 
 
def _find_cc_license_links(soup):
    links = soup.find_all("a", href=True)
    return [a for a in links if any(domain in a["href"].lower() for domain in CC_LICENSE_DOMAINS)]
 
 
def _find_caption_license_mentions(soup):
    figcaptions = soup.find_all("figcaption")
    mentions = 0
    for fc in figcaptions:
        text = fc.get_text(" ", strip=True).lower()
        if any(re.search(pattern, text) for pattern in CC_LICENSE_TEXT_PATTERNS):
            mentions += 1
    return mentions
 
 
def analyze_open_image_licensing(site_data):
 
    soup = site_data.soup
    images = soup.find_all("img")
    total_images = len(images)
 
    if total_images == 0:
        return {
            "factor": "Open Image Licensing",
            "score": 70,  # no images -- not applicable, not penalized
            "status": "Average",
            "details": {"total_images": 0},
            "recommendations": []
        }
 
    rel_license_links = _find_rel_license_links(soup)
    cc_license_links = _find_cc_license_links(soup)
    caption_license_mentions = _find_caption_license_mentions(soup)
    json_ld_licensed_images = _extract_json_ld_image_licenses(soup)
 
    cc_licensed_via_schema = [img for img in json_ld_licensed_images if img["is_creative_commons"]]
    all_rights_reserved_via_schema = [
        img for img in json_ld_licensed_images
        if not img["is_creative_commons"] and img.get("license")
    ]
 
    page_text_lower = soup.get_text(" ", strip=True).lower()
    all_rights_reserved_mentioned = any(
        re.search(pattern, page_text_lower) for pattern in ALL_RIGHTS_RESERVED_PATTERNS
    )
 
    has_any_open_license_signal = bool(
        cc_license_links or caption_license_mentions or cc_licensed_via_schema or rel_license_links
    )
 
    licensing_signal_count = (
        len(cc_license_links) + caption_license_mentions
        + len(cc_licensed_via_schema) + len(rel_license_links)
    )
 
    # rough coverage estimate: how many images have *some* explicit license signal
    # vs total images on the page (schema-based signals map most directly to specific images)
    images_with_explicit_license = len(json_ld_licensed_images)
    pct_images_licensed = (images_with_explicit_license / total_images * 100) if total_images else 0
 
    score = 0
 
    if has_any_open_license_signal:
        score += 40
        score += min(licensing_signal_count, 8) * 5
        score += round(pct_images_licensed * 0.2)
 
        if all_rights_reserved_via_schema and not cc_licensed_via_schema:
            score -= 10
    elif all_rights_reserved_mentioned:
        score = 15
    else:
        # no licensing information declared either way -- default assumption is
        # all-rights-reserved, which is the least reusable/citable state
        score = 25
 
    score = max(0, min(score, 100))
 
    details = {
        "total_images": total_images,
        "rel_license_links": len(rel_license_links),
        "creative_commons_license_links": len(cc_license_links),
        "caption_cc_mentions": caption_license_mentions,
        "images_with_explicit_schema_license": images_with_explicit_license,
        "images_licensed_cc_via_schema": len(cc_licensed_via_schema),
        "images_all_rights_reserved_via_schema": len(all_rights_reserved_via_schema),
        "all_rights_reserved_language_detected": all_rights_reserved_mentioned,
        "pct_images_with_declared_license": round(pct_images_licensed, 1)
    }
 
    recommendations = []
 
    if score < 75:
 
        if not has_any_open_license_signal:
            recommendations.append(
                "No open licensing (e.g. Creative Commons) information was found for images on this page — "
                "openly licensed images are reused and cited far more often than all-rights-reserved imagery."
            )
 
        if images_with_explicit_license < total_images:
            recommendations.append(
                "Add ImageObject structured data with an explicit \"license\" field for each image, ideally "
                "linking to a Creative Commons license URL (e.g. https://creativecommons.org/licenses/by/4.0/)."
            )
 
        if all_rights_reserved_via_schema and not cc_licensed_via_schema:
            recommendations.append(
                "Images are explicitly marked all-rights-reserved in schema — consider licensing key images "
                "under Creative Commons to increase reuse and citation potential."
            )
 
        if caption_license_mentions == 0 and not cc_license_links:
            recommendations.append(
                "Add visible license attribution near images (e.g. in figcaptions) stating the license "
                "(e.g. \"CC BY 4.0\") and linking to the license terms."
            )
 
    return {
        "factor": "Open Image Licensing",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_open_image_licensing