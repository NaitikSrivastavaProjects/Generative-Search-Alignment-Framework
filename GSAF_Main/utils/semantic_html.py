import re


def analyze_semantic_html(site_data):

    soup = site_data.soup

    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")
    h3 = soup.find_all("h3")

    score = 100

    recommendations = []

    details = {
        "h1_count": len(h1),
        "h2_count": len(h2),
        "h3_count": len(h3),
        "heading_order_valid": True
    }

    if len(h1) == 0:
        score -= 35
        recommendations.append(
            "Add a primary H1 heading."
        )

    elif len(h1) > 1:
        score -= 20
        recommendations.append(
            "Use only one H1 heading per page."
        )

    if len(h2) == 0:
        score -= 20
        recommendations.append(
            "Organize content using H2 headings."
        )

    if len(h3) == 0:
        score -= 10
        recommendations.append(
            "Use H3 headings for deeper content hierarchy."
        )

    headings = soup.find_all(
        ["h1", "h2", "h3"]
    )

    previous = 0

    for heading in headings:

        level = int(heading.name[1])

        if previous != 0 and level > previous + 1:

            details["heading_order_valid"] = False

            score -= 15

            recommendations.append(
                "Avoid skipping heading levels (for example H1 directly to H3)."
            )

            break

        previous = level

    score = max(0, min(score, 100))

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }