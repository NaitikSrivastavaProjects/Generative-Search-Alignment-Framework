def analyze_list_structure(site_data):

    soup = site_data.soup

    ul_count = len(
        soup.find_all("ul")
    )

    ol_count = len(
        soup.find_all("ol")
    )

    li_count = len(
        soup.find_all("li")
    )

    paragraphs = len(
        soup.find_all("p")
    )

    score = 0

    score += min(ul_count + ol_count, 10) * 6
    score += min(li_count, 30) * 2

    if paragraphs > 0:

        ratio = li_count / paragraphs

        if ratio >= 0.40:
            score += 20

        elif ratio >= 0.20:
            score += 10

    score = min(score, 100)

    details = {
        "unordered_lists": ul_count,
        "ordered_lists": ol_count,
        "list_items": li_count,
        "paragraphs": paragraphs
    }

    recommendations = []

    if score < 75:

        if ul_count + ol_count == 0:
            recommendations.append(
                "Use bullet points or numbered lists to improve AI readability."
            )

        if li_count < 10:
            recommendations.append(
                "Convert lengthy paragraphs into concise bullet points where appropriate."
            )

        if paragraphs > 10 and li_count == 0:
            recommendations.append(
                "Break large text blocks into structured lists."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }