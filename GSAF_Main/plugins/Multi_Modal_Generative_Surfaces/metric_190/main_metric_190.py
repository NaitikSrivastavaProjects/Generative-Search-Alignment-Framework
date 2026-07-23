import re
from urllib.parse import urlparse, unquote
 
 
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif")
 
# filenames that are clearly camera/screenshot/CMS-generated defaults, not authored
GENERIC_FILENAME_PATTERNS = [
    r"^img[-_]?\d+$",
    r"^image[-_]?\d+$",
    r"^dsc[-_]?\d+$",
    r"^dscn\d+$",
    r"^photo[-_]?\d+$",
    r"^screenshot.*\d*$",
    r"^screen[-_]?shot.*$",
    r"^untitled.*$",
    r"^\d+$",
    r"^[a-f0-9]{8,}$",              # bare hex hash (e.g. CDN-generated ids)
    r"^[a-f0-9]{6,}[-_][a-f0-9]{4,}",  # uuid-ish / hash-with-suffix
]
 
MIN_DESCRIPTIVE_WORDS = 2
MAX_REASONABLE_WORDS = 12
 
 
def _get_filename_stem(src):
    parsed = urlparse(src)
    path = unquote(parsed.path)
    filename = path.rsplit("/", 1)[-1]
 
    if not filename.lower().endswith(IMAGE_EXTENSIONS):
        return None
 
    stem = re.sub(r"\.[a-zA-Z0-9]+$", "", filename)
    return stem
 
 
def _split_words(stem):
    # split on common separators used in descriptive filenames
    words = re.split(r"[-_\s]+", stem)
    return [w for w in words if w]
 
 
def _is_generic(stem):
    lower = stem.lower()
    return any(re.match(pattern, lower) for pattern in GENERIC_FILENAME_PATTERNS)
 
 
def analyze_image_filenames(site_data):
 
    soup = site_data.soup
    images = soup.find_all("img")
 
    total_images = 0
    generic_filenames = 0
    too_few_words = 0
    keyword_stuffed = 0
    descriptive_filenames = 0
    non_image_or_unparseable = 0
 
    filename_stems_seen = []
    example_generic = []
 
    for img in images:
        src = img.get("src") or img.get("data-src")
        if not src:
            non_image_or_unparseable += 1
            continue
 
        stem = _get_filename_stem(src)
        if stem is None:
            non_image_or_unparseable += 1
            continue
 
        total_images += 1
 
        if _is_generic(stem):
            generic_filenames += 1
            if len(example_generic) < 5:
                example_generic.append(stem)
            continue
 
        words = _split_words(stem)
        real_words = [w for w in words if not w.isdigit()]
 
        if len(real_words) < MIN_DESCRIPTIVE_WORDS:
            too_few_words += 1
            continue
 
        if len(words) > MAX_REASONABLE_WORDS:
            keyword_stuffed += 1
            continue
 
        descriptive_filenames += 1
        filename_stems_seen.append(stem.lower())
 
    duplicate_filenames = len(filename_stems_seen) - len(set(filename_stems_seen))
 
    pct_descriptive = (descriptive_filenames / total_images * 100) if total_images else 0
 
    score = 0
 
    if total_images > 0:
        score += round(pct_descriptive * 0.8)
        score += min(total_images, 10) * 1
 
        if duplicate_filenames > 0:
            score -= min(duplicate_filenames, 10) * 3
    else:
        score = 70  # no images to evaluate -- not applicable, not penalized
 
    score = max(0, min(score, 100))
 
    details = {
        "total_images_evaluated": total_images,
        "descriptive_filenames": descriptive_filenames,
        "generic_filenames": generic_filenames,
        "example_generic_filenames": example_generic,
        "filenames_too_few_words": too_few_words,
        "filenames_keyword_stuffed": keyword_stuffed,
        "duplicate_filenames": duplicate_filenames,
        "pct_descriptive": round(pct_descriptive, 1)
    }
 
    recommendations = []
 
    if score < 75:
 
        if generic_filenames > 0:
            recommendations.append(
                f"{generic_filenames} image(s) use generic, camera/CMS-default filenames "
                f"(e.g. {', '.join(example_generic[:3]) if example_generic else 'IMG_1234.jpg'}) — rename to "
                "descriptive, hyphen-separated filenames (e.g. \"red-velvet-cake-slice.jpg\") since these are "
                "cited directly in image-grounded answers."
            )
 
        if too_few_words > 0:
            recommendations.append(
                f"{too_few_words} image filename(s) are too short to be descriptive — use at least "
                f"{MIN_DESCRIPTIVE_WORDS} meaningful, hyphen-separated words."
            )
 
        if keyword_stuffed > 0:
            recommendations.append(
                f"{keyword_stuffed} image filename(s) are excessively long — keep filenames concise and natural, "
                "not stuffed with keywords."
            )
 
        if duplicate_filenames > 0:
            recommendations.append(
                "Multiple images share the same filename stem — use unique, specific filenames for each distinct image."
            )
 
        if total_images == 0:
            recommendations.append(
                "No images with parseable filenames were found — ensure images are served with clean, "
                "descriptive filenames rather than query-string-only or dynamically hashed URLs."
            )
 
    return {
        "factor": "Image File Names (Descriptive)",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_image_filenames