import re
 
 
# generic/low-value alt text that reads as a placeholder rather than a description
GENERIC_ALT_PATTERNS = [
    r"^image$", r"^photo$", r"^picture$", r"^img$", r"^untitled$",
    r"^dsc\d*", r"^img[-_]?\d+", r"^image[-_]?\d+", r"^photo[-_]?\d+",
    r"^screenshot", r"^\d+$"
]
 
# filenames leaking through as alt text (e.g. alt="banner-final-v2.jpg")
FILENAME_PATTERN = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|bmp)$", re.IGNORECASE)
 
MIN_DESCRIPTIVE_WORDS = 3
MAX_REASONABLE_WORDS = 25
 
 
def _is_generic(alt_text):
    lower = alt_text.strip().lower()
    return any(re.match(pattern, lower) for pattern in GENERIC_ALT_PATTERNS)
 
 
def _is_decorative(img_tag):
    role = (img_tag.get("role") or "").lower()
    alt = img_tag.get("alt")
    return role == "presentation" or alt == ""
 
 
def analyze_image_alt_text_quality(site_data):
 
    soup = site_data.soup
    images = soup.find_all("img")
 
    total_images = len(images)
 
    missing_alt = 0
    decorative_images = 0
    generic_alt = 0
    filename_as_alt = 0
    too_short = 0
    keyword_stuffed = 0
    descriptive_alt = 0
 
    alt_texts_seen = []
 
    for img in images:
        alt = img.get("alt")
 
        if alt is None:
            missing_alt += 1
            continue
 
        alt_stripped = alt.strip()
 
        if _is_decorative(img):
            decorative_images += 1
            continue
 
        if alt_stripped == "":
            missing_alt += 1
            continue
 
        if FILENAME_PATTERN.search(alt_stripped):
            filename_as_alt += 1
            continue
 
        if _is_generic(alt_stripped):
            generic_alt += 1
            continue
 
        word_count = len(alt_stripped.split())
 
        if word_count < MIN_DESCRIPTIVE_WORDS:
            too_short += 1
            continue
 
        if word_count > MAX_REASONABLE_WORDS:
            keyword_stuffed += 1
            continue
 
        descriptive_alt += 1
        alt_texts_seen.append(alt_stripped.lower())
 
    duplicate_alt_texts = len(alt_texts_seen) - len(set(alt_texts_seen))
 
    # denominator excludes legitimately decorative images, since those are
    # correctly using empty alt and shouldn't be judged on description quality
    evaluable_images = total_images - decorative_images
    pct_descriptive = (descriptive_alt / evaluable_images * 100) if evaluable_images else 0
 
    score = 0
 
    if evaluable_images > 0:
        score += round(pct_descriptive * 0.7)
        score += min(evaluable_images, 10) * 1  # small bonus for having images to describe at all
 
        if duplicate_alt_texts > 0:
            score -= min(duplicate_alt_texts, 10) * 3
    else:
        score = 70  # no evaluable images on the page -- not applicable, not penalized
 
    score = max(0, min(score, 100))
 
    details = {
        "total_images": total_images,
        "decorative_images_correctly_empty": decorative_images,
        "missing_alt_text": missing_alt,
        "generic_alt_text": generic_alt,
        "filename_leaked_as_alt": filename_as_alt,
        "alt_text_too_short": too_short,
        "alt_text_keyword_stuffed": keyword_stuffed,
        "descriptive_alt_text": descriptive_alt,
        "duplicate_alt_texts": duplicate_alt_texts,
        "pct_descriptive": round(pct_descriptive, 1)
    }
 
    recommendations = []
 
    if score < 75:
 
        if missing_alt > 0:
            recommendations.append(
                f"{missing_alt} image(s) are missing alt text entirely — multi-modal LLMs treat alt text as the "
                "canonical description, so images without it are effectively invisible to them."
            )
 
        if generic_alt > 0:
            recommendations.append(
                f"{generic_alt} image(s) use generic alt text (e.g. \"image\", \"photo\") — replace with specific, "
                "descriptive text about what the image actually shows."
            )
 
        if filename_as_alt > 0:
            recommendations.append(
                f"{filename_as_alt} image(s) have a raw filename as alt text (e.g. \"banner-final.jpg\") — "
                "write a real description instead."
            )
 
        if too_short > 0:
            recommendations.append(
                f"{too_short} image(s) have alt text that's too brief to be descriptive — aim for at least "
                f"{MIN_DESCRIPTIVE_WORDS} words that convey the image's content and context."
            )
 
        if keyword_stuffed > 0:
            recommendations.append(
                f"{keyword_stuffed} image(s) have unusually long alt text — keep it concise and natural "
                "rather than stuffing in keywords."
            )
 
        if duplicate_alt_texts > 0:
            recommendations.append(
                "Multiple images share identical alt text — write unique descriptions for each distinct image."
            )
 
    return {
        "factor": "Image Alt Text Quality",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_image_alt_text_quality