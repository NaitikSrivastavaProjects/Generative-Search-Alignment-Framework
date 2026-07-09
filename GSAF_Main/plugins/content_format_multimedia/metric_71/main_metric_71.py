from models.metric_result import MetricResult
from utils.helpers import get_status


FILENAME_PATTERNS = [".jpg", ".jpeg", ".png", ".gif", ".webp", "img_", "image_", "photo_"]


def is_quality_alt(alt_text):
    if not alt_text or len(alt_text.strip()) < 5:
        return False
    alt_lower = alt_text.lower()
    if any(p in alt_lower for p in FILENAME_PATTERNS):
        return False
    if len(alt_text.split()) < 3:
        return False
    return True


def run(site_data):
    result = MetricResult(factor="71 - Image Alt Text as Answer Caption")

    try:
        soup = site_data.soup
        images = soup.find_all("img")

        if not images:
            result.status = "Not Applicable"
            result.details["note"] = "No images found on this page."
            return result.to_dict()

        quality_alts = []
        missing_alts = []
        low_quality_alts = []

        for img in images:
            alt = img.get("alt", "")
            src = img.get("src", "")
            if not alt:
                missing_alts.append(src[:80])
            elif is_quality_alt(alt):
                quality_alts.append(alt)
            else:
                low_quality_alts.append(alt)

        total = len(images)
        result.details["total_images"] = total
        result.details["quality_alt_count"] = len(quality_alts)
        result.details["missing_alt_count"] = len(missing_alts)
        result.details["low_quality_alt_count"] = len(low_quality_alts)

        result.score = round((len(quality_alts) / total) * 100)
        result.status = get_status(result.score)

        if missing_alts:
            result.recommendations.append(
                f"{len(missing_alts)} image(s) have no alt text — add descriptive alt text to each."
            )
        if low_quality_alts:
            result.recommendations.append(
                f"{len(low_quality_alts)} image(s) have low-quality alt text (filenames or single words). "
                "Use descriptive phrases that explain what the image shows."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()