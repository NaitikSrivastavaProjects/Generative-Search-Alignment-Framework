from models.metric_result import MetricResult
from utils.helpers import get_status


AUDIO_EXTENSIONS = [".mp3", ".wav", ".ogg", ".m4a"]
CONTENT_TYPE_SIGNALS = [
    "glossary", "dictionary", "pronunciation", "medical",
    "scientific", "terminology", "terms", "definition"
]


def run(site_data):
    result = MetricResult(factor="76 - Pronunciation Audio")

    try:
        soup = site_data.soup
        url_lower = site_data.url.lower()
        title = soup.find("title")
        title_text = title.get_text().lower() if title else ""

        is_relevant_content = any(
            s in url_lower or s in title_text for s in CONTENT_TYPE_SIGNALS
        )

        if not is_relevant_content:
            result.status = "Not Applicable"
            result.details["note"] = (
                "Pronunciation audio is only relevant for medical, scientific, "
                "or glossary content. Not applicable for this page type."
            )
            return result.to_dict()

        audio_tags = soup.find_all("audio")
        audio_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if any(a["href"].lower().endswith(ext) for ext in AUDIO_EXTENSIONS)
        ]
        audio_schema = [
            b for b in site_data.json_ld
            if b.get("@type") == "AudioObject"
        ]

        result.details["audio_tags_found"] = len(audio_tags)
        result.details["audio_file_links"] = len(audio_links)
        result.details["audio_schema_found"] = len(audio_schema)

        if audio_tags or audio_schema:
            result.score = 100
        elif audio_links:
            result.score = 60
            result.recommendations.append(
                "Audio file links found but no audio tag or schema. "
                "Use proper audio tags and AudioObject schema for better voice assistant support."
            )
        else:
            result.score = 0
            result.recommendations.append(
                "No pronunciation audio found. For terminology-heavy content, "
                "adding audio clips improves voice assistant answer eligibility."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()