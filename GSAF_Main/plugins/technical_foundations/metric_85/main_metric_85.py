from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import OVERLAY_CLASS_PATTERNS


def run(site_data):
    result = MetricResult(factor="85 - Avoid Interstitials Above Answer")

    try:
        soup = site_data.soup

        overlay_elements = soup.find_all(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in OVERLAY_CLASS_PATTERNS)
        )

        main_content = soup.find(["article", "main"]) or soup.find("div", class_="content")

        overlays_before_content = []
        overlays_after_content = []

        all_elements = list(soup.descendants)

        for overlay in overlay_elements:
            has_fixed_style = "position:fixed" in (overlay.get("style", "").replace(" ", "").lower())
            has_fixed_style = has_fixed_style or "position:absolute" in (overlay.get("style", "").replace(" ", "").lower())

            if main_content:
                try:
                    overlay_idx = all_elements.index(overlay)
                    content_idx = all_elements.index(main_content)
                    if overlay_idx < content_idx and has_fixed_style:
                        overlays_before_content.append(overlay.get("class", []))
                    else:
                        overlays_after_content.append(overlay.get("class", []))
                except ValueError:
                    overlays_after_content.append(overlay.get("class", []))
            else:
                if has_fixed_style:
                    overlays_before_content.append(overlay.get("class", []))

        result.details["overlays_found"] = len(overlay_elements)
        result.details["overlays_before_content"] = len(overlays_before_content)
        result.details["overlays_after_content"] = len(overlays_after_content)

        if not overlay_elements:
            result.score = 100
        elif overlays_before_content:
            result.score = 0
            result.recommendations.append(
                f"Found {len(overlays_before_content)} overlay element(s) positioned before main content. "
                "Interstitials above the answer disqualify pages from answer box eligibility."
            )
        elif overlays_after_content:
            result.score = 60
            result.recommendations.append(
                "Overlay elements detected but positioned after main content — lower risk but worth reviewing."
            )
        else:
            result.score = 70

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()