import re
from models.metric_result import MetricResult
from utils.helpers import get_status


TIMESTAMP_PATTERN = re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b')
VIDEO_PROVIDERS = ["youtube.com", "vimeo.com", "youtu.be"]


def run(site_data):
    result = MetricResult(factor="74 - Timestamped Video Chapters")

    try:
        soup = site_data.soup

        video_iframes = [
            i for i in soup.find_all("iframe", src=True)
            if any(p in i["src"].lower() for p in VIDEO_PROVIDERS)
        ]
        video_tags = soup.find_all("video")
        has_video = bool(video_iframes or video_tags)

        if not has_video:
            result.status = "Not Applicable"
            result.details["note"] = "No video found — timestamped chapters not applicable."
            return result.to_dict()

        clip_schema = [
            b for b in site_data.json_ld
            if b.get("@type") in ("Clip", "SeekToAction")
        ]

        page_text = soup.get_text()
        timestamps = TIMESTAMP_PATTERN.findall(page_text)
        unique_timestamps = list(set(timestamps))

        result.details["clip_schema_found"] = len(clip_schema)
        result.details["timestamps_in_text"] = len(unique_timestamps)
        result.details["timestamp_examples"] = unique_timestamps[:5]

        if clip_schema:
            result.score = min(100, 60 + len(unique_timestamps) * 10)
        elif unique_timestamps:
            result.score = min(60, len(unique_timestamps) * 10)
            result.recommendations.append(
                "Timestamps found in text but no Clip schema detected. "
                "Add SeekToAction or Clip schema for Key Moments eligibility in search results."
            )
        else:
            result.score = 0
            result.recommendations.append(
                "No timestamped chapters found. Add chapter markers to improve answer box eligibility."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()