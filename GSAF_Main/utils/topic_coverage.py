import re


SECTION_HEADINGS = [
    "introduction",
    "overview",
    "benefits",
    "advantages",
    "disadvantages",
    "features",
    "examples",
    "best practices",
    "use cases",
    "implementation",
    "conclusion",
    "summary",
    "faq",
    "references"
]


def analyze_topic_coverage(site_data):

    text = site_data.soup.get_text(" ", strip=True)

    lower_text = text.lower()

    word_count = len(text.split())

    heading_count = 0

    for heading in SECTION_HEADINGS:
        heading_count += lower_text.count(heading)

    heading_tags = len(
        site_data.soup.find_all(
            ["h1", "h2", "h3", "h4"]
        )
    )

    list_items = len(
        site_data.soup.find_all("li")
    )

    paragraph_count = len(
        site_data.soup.find_all("p")
    )

    score = 0

    score += min(word_count // 200, 10) * 5
    score += min(heading_count, 8) * 4
    score += min(heading_tags, 10) * 2
    score += min(list_items, 20) * 1
    score += min(paragraph_count, 20) * 1

    score = min(score, 100)

    details = {
        "word_count": word_count,
        "section_headings": heading_count,
        "heading_tags": heading_tags,
        "paragraphs": paragraph_count,
        "list_items": list_items
    }

    recommendations = []

    if score < 75:

        if word_count < 2000:
            recommendations.append(
                "Expand the content to provide more comprehensive topic coverage."
            )

        if heading_tags < 5:
            recommendations.append(
                "Break the content into more structured sections using headings."
            )

        if list_items < 5:
            recommendations.append(
                "Include lists, key takeaways or FAQs for better coverage."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }