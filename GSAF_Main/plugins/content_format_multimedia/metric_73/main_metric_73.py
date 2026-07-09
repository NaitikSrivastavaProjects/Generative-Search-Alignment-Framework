from models.metric_result import MetricResult
from utils.helpers import get_status


VIDEO_PROVIDERS = ["youtube.com", "vimeo.com", "youtu.be"]
TRANSCRIPT_PATTERNS = ["transcript", "caption", "subtitles"]


def run(site_data):
    result = MetricResult(factor="73 - Short Video Clips with Transcripts")

    try:
        soup = site_data.soup

        video_tags = soup.find_all("video")
        video_iframes = [
            i for i in soup.find_all("iframe", src=True)
            if any(p in i["src"].lower() for p in VIDEO_PROVIDERS)
        ]

        video_schema = [
            b for b in site_data.json_ld
            if b.get("@type") == "VideoObject"
        ]

        has_video = bool(video_tags or video_iframes or video_schema)

        result.details["video_tags_found"] = len(video_tags)
        result.details["video_iframes_found"] = len(video_iframes)
        result.details["video_schema_found"] = len(video_schema)

        if not has_video:
            result.status = "Not Applicable"
            result.details["note"] = "No video content found on this page."
            return result.to_dict()

        transcript_element = soup.find(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in TRANSCRIPT_PATTERNS)
        )

        schema_has_transcript = any(
            "transcript" in str(b).lower() for b in video_schema
        )

        has_transcript = bool(transcript_element or schema_has_transcript)
        result.details["transcript_found"] = has_transcript

        if has_transcript:
            result.score = 100
        else:
            result.score = 40
            result.recommendations.append(
                "Video found but no transcript detected. "
                "Add a transcript to make video content accessible to answer engine crawlers."
            )
            result.details["note"] = (
                "If transcript is dynamically loaded, ensure it is server-side rendered."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()