def analyze_self_contained_sections(site_data):

    soup = site_data.soup

    headings = soup.find_all(
        ["h2", "h3"]
    )

    score = 100

    details = {
        "sections": len(headings),
        "self_contained_sections": 0,
        "average_section_words": 0
    }

    recommendations = []

    total_words = 0

    valid_sections = 0

    for heading in headings:

        words = 0

        sibling = heading.find_next_sibling()

        while sibling and sibling.name not in [
            "h2",
            "h3"
        ]:

            words += len(
                sibling.get_text(
                    " ",
                    strip=True
                ).split()
            )

            sibling = sibling.find_next_sibling()

        total_words += words

        if words >= 50:

            valid_sections += 1

    details["self_contained_sections"] = valid_sections

    if len(headings) > 0:

        details["average_section_words"] = round(
            total_words / len(headings),
            2
        )

    if len(headings) == 0:

        score -= 50

        recommendations.append(
            "Divide content into meaningful sections using H2 and H3 headings."
        )

    else:

        ratio = valid_sections / len(headings)

        if ratio < 0.5:

            score -= 40

            recommendations.append(
                "Expand sections so each heading contains sufficient standalone content."
            )

        elif ratio < 0.8:

            score -= 20

            recommendations.append(
                "Some sections are too short to stand alone."
            )

    score = max(0, min(score, 100))

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }