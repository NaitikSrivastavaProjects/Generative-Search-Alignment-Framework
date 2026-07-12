from models.metric_result import MetricResult
from utils.helpers import get_status


COMMENT_CLASS_PATTERNS = [
    "comment", "comments", "discussion",
    "replies", "disqus", "livefyre"
]

QA_SCHEMA_TYPES = ["QAPage", "Question", "Answer"]


def run(site_data):
    result = MetricResult(factor="100 - User Submitted Q&A Activity")

    try:
        soup = site_data.soup

        comment_section = soup.find(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in COMMENT_CLASS_PATTERNS)
        )

        disqus_embed = soup.find("div", id="disqus_thread")
        comment_count = 0
        if comment_section:
            comment_items = comment_section.find_all(
                class_=lambda x: x and "comment" in " ".join(x).lower()
            )
            comment_count = len(comment_items)

        qa_schema = []
        for block in site_data.json_ld:
            if block.get("@type") in QA_SCHEMA_TYPES:
                qa_schema.append(block.get("@type"))

        result.details["comment_section_found"] = bool(comment_section)
        result.details["disqus_embed_found"] = bool(disqus_embed)
        result.details["comment_count"] = comment_count
        result.details["qa_schema_types"] = qa_schema

        if qa_schema and comment_count > 0:
            result.score = 100
        elif comment_count > 5:
            result.score = 70
        elif comment_section or disqus_embed:
            result.score = 40
        elif qa_schema:
            result.score = 60
        else:
            result.score = 0
            result.recommendations.append(
                "No comment section or Q&A community found. "
                "Adding user-generated discussion increases answer trust signals."
            )

        result.status = get_status(result.score)

        if comment_section and not qa_schema:
            result.recommendations.append(
                "Comments section exists but no QAPage schema found. "
                "Add QAPage schema markup to improve answer box eligibility."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()