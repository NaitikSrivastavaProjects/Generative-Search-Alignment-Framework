from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import STRONG_CREDENTIALS, MODERATE_CREDENTIALS, WEAK_CREDENTIALS
from utils.constants import AUTHOR_CLASS_PATTERNS


def run(site_data):
    result = MetricResult(factor="61 - Author Bio with Credentials")

    try:
        soup = site_data.soup

        author_section = soup.find(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in AUTHOR_CLASS_PATTERNS)
        )

        if not author_section:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "No author section found — add an author bio with credentials near the article content."
            )
            return result.to_dict()

        text = author_section.get_text().lower()
        result.details["author_section_found"] = True
        result.details["bio_length"] = len(text.split())

        strong_found = [kw for kw in STRONG_CREDENTIALS if kw in text]
        moderate_found = [kw for kw in MODERATE_CREDENTIALS if kw in text]
        weak_found = [kw for kw in WEAK_CREDENTIALS if kw in text]

        result.details["strong_credentials"] = strong_found
        result.details["moderate_credentials"] = moderate_found

        if strong_found:
            result.score = 70
        elif moderate_found:
            result.score = 40
        elif weak_found:
            result.score = 15
        else:
            result.score = 10

        # bonus for bio placed inside article/main rather than footer
        article = soup.find(["article", "main"])
        if article and article.find(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in AUTHOR_CLASS_PATTERNS)
        ):
            result.score = min(100, result.score + 30)
            result.details["bio_near_content"] = True
        else:
            result.details["bio_near_content"] = False

        result.status = get_status(result.score)
        result.details["note"] = "Credential presence is scored, not validity — cannot verify claims without external registries."

        if not strong_found and not moderate_found:
            result.recommendations.append(
                "Author bio lacks strong credentials. Add professional qualifications, "
                "certifications, or years of experience to improve E-E-A-T signals."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()