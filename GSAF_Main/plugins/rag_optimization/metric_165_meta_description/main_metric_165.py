from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):

    soup = site_data.soup
    keyword = site_data.keyword.lower().strip() if site_data.keyword else ""

    score = 0
    details = {}
    recommendations = []

    # ----------------------------------------
    # Find Meta Description
    # ----------------------------------------

    meta = soup.find("meta", attrs={"name": "description"})

    if meta and meta.get("content"):

        description = meta["content"].strip()

        details["description"] = description
        details["length"] = len(description)

        # ----------------------------------------
        # Meta Exists (30)
        # ----------------------------------------

        score += 30

        # ----------------------------------------
        # Length Check (30)
        # ----------------------------------------

        length = len(description)

        if 120 <= length <= 160:
            score += 30

        elif 80 <= length < 120:
            score += 20
            recommendations.append(
                "Increase meta description length to around 120–160 characters."
            )

        elif 160 < length <= 180:
            score += 20
            recommendations.append(
                "Meta description is slightly long."
            )

        else:
            recommendations.append(
                "Meta description should ideally be between 120 and 160 characters."
            )

        # ----------------------------------------
        # Keyword Presence (20)
        # ----------------------------------------

        if keyword:

            if keyword in description.lower():

                score += 20

            else:

                recommendations.append(
                    "Include the target keyword in the meta description."
                )

        else:

            score += 20

        # ----------------------------------------
        # Duplicate Words Check (10)
        # ----------------------------------------

        words = description.lower().split()

        unique_ratio = len(set(words)) / max(len(words), 1)

        details["unique_word_ratio"] = round(unique_ratio, 2)

        if unique_ratio >= 0.8:

            score += 10

        else:

            recommendations.append(
                "Avoid excessive repetition in the meta description."
            )

        # ----------------------------------------
        # Ends Properly (10)
        # ----------------------------------------

        if description.endswith((".", "!", "?")):

            score += 10

        else:

            recommendations.append(
                "End the meta description with proper punctuation."
            )

    else:

        details["description"] = "Not Found"

        recommendations.append(
            "Add a meta description to improve AI and search understanding."
        )

    return MetricResult(
        factor="Metric 165 - Meta Description Quality",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()