import re
import json
 
 
VIDEO_EMBED_DOMAINS = [
    "youtube.com", "youtube-nocookie.com", "youtu.be",
    "vimeo.com", "wistia.com", "wistia.net", "loom.com"
]
 
TRANSCRIPT_HEADING_PATTERNS = [
    "transcript",
    "video transcript",
    "full transcript",
    "read the transcript",
    "show transcript"
]
 
CAPTION_TRACK_KINDS = ["captions", "subtitles"]
 
MIN_TRANSCRIPT_WORDS = 50  # below this, it reads as a stub/placeholder, not a real transcript
 
 
def _get_native_videos(soup):
    return soup.find_all("video")
 
 
def _get_embedded_videos(soup):
    embeds = []
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"].lower()
        if any(domain in src for domain in VIDEO_EMBED_DOMAINS):
            embeds.append(iframe)
    return embeds
 
 
def _has_caption_track(video_tag):
    tracks = video_tag.find_all("track")
    return any((t.get("kind") or "").lower() in CAPTION_TRACK_KINDS for t in tracks)
 
 
def _find_transcript_section(soup):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "summary", "button"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if any(pattern in heading_text for pattern in TRANSCRIPT_HEADING_PATTERNS):
            return heading
    return None
 
 
def _extract_transcript_text(transcript_heading):
    if transcript_heading is None:
        return ""
 
    text_parts = []
    for sibling in transcript_heading.find_all_next():
        if sibling.name in ["h1", "h2", "h3", "h4"]:
            break
        if sibling.name in ["p", "div", "li", "span"]:
            text = sibling.get_text(" ", strip=True)
            if text:
                text_parts.append(text)
        if len(" ".join(text_parts).split()) > 500:
            break
 
    return " ".join(text_parts)
 
 
def _get_video_object_schema_has_transcript(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("@type") == "VideoObject":
                if block.get("transcript") or block.get("caption"):
                    return True
    return False
 
 
def analyze_video_transcripts(site_data):
 
    soup = site_data.soup
 
    native_videos = _get_native_videos(soup)
    embedded_videos = _get_embedded_videos(soup)
    total_videos = len(native_videos) + len(embedded_videos)
 
    native_videos_with_captions = sum(1 for v in native_videos if _has_caption_track(v))
 
    transcript_heading = _find_transcript_section(soup)
    transcript_text = _extract_transcript_text(transcript_heading)
    transcript_word_count = len(transcript_text.split())
    has_substantial_transcript = transcript_word_count >= MIN_TRANSCRIPT_WORDS
 
    schema_indicates_transcript = _get_video_object_schema_has_transcript(soup)
 
    has_any_caption_or_transcript_signal = (
        native_videos_with_captions > 0
        or has_substantial_transcript
        or schema_indicates_transcript
    )
 
    score = 0
 
    if total_videos > 0:
        if native_videos:
            pct_native_captioned = native_videos_with_captions / len(native_videos) * 100
            score += round(pct_native_captioned * 0.4)
 
        if has_substantial_transcript:
            score += 40
        elif transcript_heading is not None:
            # a transcript section exists but is too thin to be useful
            score += 10
 
        if schema_indicates_transcript:
            score += 20
 
        if embedded_videos and not native_videos and not has_substantial_transcript:
            # embedded third-party video (e.g. YouTube) with no on-page transcript --
            # captions may exist on the platform itself but aren't ingestible from this page
            score += 5
 
        score = max(0, min(score, 100))
    else:
        score = 70  # no video content on the page -- not applicable, not penalized
 
    details = {
        "native_video_elements": len(native_videos),
        "native_videos_with_caption_track": native_videos_with_captions,
        "embedded_third_party_videos": len(embedded_videos),
        "transcript_section_found": transcript_heading is not None,
        "transcript_word_count": transcript_word_count,
        "substantial_transcript_present": has_substantial_transcript,
        "video_object_schema_has_transcript": schema_indicates_transcript
    }
 
    recommendations = []
 
    if total_videos > 0 and score < 75:
 
        if not has_any_caption_or_transcript_signal:
            recommendations.append(
                "No captions or transcript were found for the video content on this page — transcripts are the "
                "primary surface multi-modal LLMs use to ingest video content, so add a full text transcript."
            )
 
        if native_videos and native_videos_with_captions < len(native_videos):
            recommendations.append(
                "Add a <track kind=\"captions\"> (WebVTT) file to native <video> elements that don't have one."
            )
 
        if transcript_heading is not None and not has_substantial_transcript:
            recommendations.append(
                f"A transcript section exists but is too short ({transcript_word_count} words) to be a real "
                "transcript — publish the full spoken text of the video."
            )
 
        if embedded_videos and not has_substantial_transcript:
            recommendations.append(
                "Embedded third-party video players (e.g. YouTube) may have their own captions, but those aren't "
                "guaranteed to be ingested from this page — publish a full transcript directly on the page as well."
            )
 
        if not schema_indicates_transcript and (native_videos or embedded_videos):
            recommendations.append(
                "Add VideoObject structured data with a transcript or caption field so the transcript is "
                "machine-readable and explicitly associated with the video."
            )
 
    return {
        "factor": "Video Transcripts (Captioned)",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_video_transcripts