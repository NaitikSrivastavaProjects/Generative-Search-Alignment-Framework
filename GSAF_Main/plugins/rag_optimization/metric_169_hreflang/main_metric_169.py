from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):

    soup = site_data.soup

    score = 0
    details = {}
    recommendations = []

    # ----------------------------------------
    # 1. Find hreflang Tags (60)
    # ----------------------------------------

    hreflang_tags = soup.find_all(
        "link",
        attrs={"rel": "alternate", "hreflang": True}
    )

    hreflang_values = []

    for tag in hreflang_tags:

        hreflang = tag.get("hreflang", "").strip()
        href = tag.get("href", "").strip()

        if hreflang and href:
            hreflang_values.append({
                "hreflang": hreflang,
                "href": href
            })

    details["hreflang_count"] = len(hreflang_values)
    details["hreflang_links"] = hreflang_values

    if len(hreflang_values) > 0:
        score += 60
    else:
        recommendations.append(
            "Add hreflang annotations for multilingual or regional versions of the page."
        )

    # ----------------------------------------
    # 2. x-default Check (20)
    # ----------------------------------------

    x_default_found = any(
        item["hreflang"].lower() == "x-default"
        for item in hreflang_values
    )

    details["x_default_found"] = x_default_found

    if x_default_found:
        score += 20
    else:
        recommendations.append(
            "Consider adding an x-default hreflang tag for users with unspecified language or region."
        )

    # ----------------------------------------
    # 3. Duplicate hreflang Values (20)
    # ----------------------------------------

    hreflang_codes = [
        item["hreflang"].lower()
        for item in hreflang_values
    ]

    duplicate_found = len(hreflang_codes) != len(set(hreflang_codes))

    details["duplicate_hreflang"] = duplicate_found

    if not duplicate_found:
        score += 20
    else:
        recommendations.append(
            "Remove duplicate hreflang values to avoid SEO conflicts."
        )

    # ----------------------------------------
    # Final Result
    # ----------------------------------------

    final_score = min(score, 100)

    return MetricResult(
        factor="Metric 169 - Hreflang",
        score=final_score,
        status=get_status(final_score),
        details=details,
        recommendations=recommendations
    ).to_dict()