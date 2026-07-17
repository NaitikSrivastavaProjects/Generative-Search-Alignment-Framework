'''
VideoObject Schema with Clip Markers Checker:
Detects whether video pages include VideoObject schema with clip
markers pointing to specific timestamps.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_video_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if "VideoObject" in types:
            found.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_video_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_video_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="24 - VideoObject Schema with Clip Markers")
    try:
        blocks = site_data.json_ld
        video_blocks = []
        for b in blocks:
            video_blocks.extend(_find_video_blocks(b))

        if not video_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No VideoObject schema found"
            result.recommendations.append("Add VideoObject schema if this page contains video content.")
            return result.to_dict()

        block = video_blocks[0]
        has_clip_markers = bool(block.get("hasPart")) or bool(block.get("clipMarker"))
        score = 100 if has_clip_markers else 50

        result.score = score
        result.status = get_status(score)
        result.details["has_video_schema"] = True
        result.details["has_clip_markers"] = has_clip_markers

        if not has_clip_markers:
            result.recommendations.append("Add 'hasPart' clip markers with timestamps pointing to key moments in the video.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()