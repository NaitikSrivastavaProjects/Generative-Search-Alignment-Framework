import re


QUESTION_STARTERS = [
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "which",
    "can",
    "should",
    "does",
    "is",
    "are"
]


def analyze_qa_subsections(site_data):

    soup = site_data.soup

    headings = soup.find_all(["h2", "h3", "h4"])

    question_sections = 0
    answer_sections = 0

    for heading in headings:

        heading_text = heading.get_text(
            " ",
            strip=True
        ).lower()

        is_question = (
            heading_text.endswith("?")
            or any(
                heading_text.startswith(word)
                for word in QUESTION_STARTERS
            )
        )

        if not is_question:
            continue

        question_sections += 1

        sibling = heading.find_next_sibling()

        while sibling and sibling.name not in [
            "h2",
            "h3",
            "h4"
        ]:

            if sibling.get_text(
                " ",
                strip=True
            ):

                answer_sections += 1
                break

            sibling = sibling.find_next_sibling()

    score = 0

    score += min(question_sections, 8) * 10
    score += min(answer_sections, 8) * 5

    score = min(score, 100)

    details = {
        "question_headings": question_sections,
        "answer_blocks": answer_sections
    }

    recommendations = []

    if score < 75:

        if question_sections == 0:

            recommendations.append(
                "Add question-based headings that match real user search queries."
            )

        if answer_sections < question_sections:

            recommendations.append(
                "Provide a direct answer immediately after every question heading."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }