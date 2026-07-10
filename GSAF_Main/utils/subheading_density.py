def analyze_subheading_density(site_data):

    soup = site_data.soup

    paragraphs = soup.find_all("p")
    headings = soup.find_all(["h2", "h3"])

    total_words = len(
        soup.get_text(" ", strip=True).split()
    )

    heading_count = len(headings)

    words_per_heading = (
        total_words / heading_count
        if heading_count
        else total_words
    )

    score = 100

    recommendations = []

    details = {
        "total_words": total_words,
        "subheadings": heading_count,
        "words_per_subheading": round(words_per_heading, 2)
    }

    if heading_count == 0:

        score = 20

        recommendations.append(
            "Add H2/H3 headings throughout the content."
        )

    elif words_per_heading > 300:

        score -= 35

        recommendations.append(
            "Add more subheadings every 200–300 words."
        )

    elif words_per_heading > 220:

        score -= 10

        recommendations.append(
            "Consider slightly increasing heading frequency."
        )

    score = max(0, min(score, 100))

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }