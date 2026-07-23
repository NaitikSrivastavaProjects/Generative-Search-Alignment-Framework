import re
import json
 
 
PODCAST_EMBED_DOMAINS = [
    "open.spotify.com", "podcasts.apple.com", "soundcloud.com",
    "buzzsprout.com", "libsyn.com", "anchor.fm", "podbean.com",
    "simplecast.com", "megaphone.fm", "transistor.fm", "captivate.fm"
]
 
TRANSCRIPT_HEADING_PATTERNS = [
    "transcript",
    "episode transcript",
    "full transcript",
    "read the transcript",
    "show transcript"
]
 
SHOW_NOTES_HEADING_PATTERNS = [
    "show notes",
    "shownotes",
    "episode notes",
    "episode summary",
    "in this episode"
]
 
TIMESTAMP_PATTERN = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
 
MIN_TRANSCRIPT_WORDS = 100  # podcast transcripts should be substantial; a stub isn't citable
MIN_SHOW_NOTES_WORDS = 30
 
 
def _get_audio_elements(soup):
    return soup.find_all("audio")
 
 
def _get_podcast_embeds(soup):
    embeds = []
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"].lower()
        if any(domain in src for domain in PODCAST_EMBED_DOMAINS):
            embeds.append(iframe)
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(domain in href for domain in PODCAST_EMBED_DOMAINS):
            embeds.append(a)
    return embeds
 
 
def _find_section_by_heading(soup, patterns):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "summary", "button"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if any(pattern in heading_text for pattern in patterns):
            return heading
    return None
 
 
def _extract_section_text(heading, max_words=600):
    if heading is None:
        return ""
 
    text_parts = []
    for sibling in heading.find_all_next():
        if sibling.name in ["h1", "h2", "h3", "h4"]:
            break
        if sibling.name in ["p", "div", "li", "span"]:
            text = sibling.get_text(" ", strip=True)
            if text:
                text_parts.append(text)
        if len(" ".join(text_parts).split()) > max_words:
            break
 
    return " ".join(text_parts)
 
 
def _get_podcast_schema_signals(soup):
    has_podcast_episode_schema = False
    schema_has_transcript = False
 
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("@type", "")
            if block_type in ("PodcastEpisode", "PodcastSeries", "AudioObject"):
                has_podcast_episode_schema = True
                if block.get("transcript"):
                    schema_has_transcript = True
 
    return has_podcast_episode_schema, schema_has_transcript
 
 
def analyze_podcast_show_notes_transcripts(site_data):
 
    soup = site_data.soup
 
    audio_elements = _get_audio_elements(soup)
    podcast_embeds = _get_podcast_embeds(soup)
    has_podcast_content = bool(audio_elements or podcast_embeds)
 
    show_notes_heading = _find_section_by_heading(soup, SHOW_NOTES_HEADING_PATTERNS)
    show_notes_text = _extract_section_text(show_notes_heading)
    show_notes_word_count = len(show_notes_text.split())
    has_substantial_show_notes = show_notes_word_count >= MIN_SHOW_NOTES_WORDS
    show_notes_has_timestamps = bool(TIMESTAMP_PATTERN.search(show_notes_text))
 
    transcript_heading = _find_section_by_heading(soup, TRANSCRIPT_HEADING_PATTERNS)
    transcript_text = _extract_section_text(transcript_heading, max_words=1000)
    transcript_word_count = len(transcript_text.split())
    has_substantial_transcript = transcript_word_count >= MIN_TRANSCRIPT_WORDS
 
    has_podcast_schema, schema_has_transcript = _get_podcast_schema_signals(soup)
 
    score = 0
 
    if has_podcast_content:
        if has_substantial_transcript:
            score += 55
        elif transcript_heading is not None:
            score += 15  # transcript section exists but too thin to be useful
 
        if has_substantial_show_notes:
            score += 20
            if show_notes_has_timestamps:
                score += 10
 
        if has_podcast_schema:
            score += 10
            if schema_has_transcript:
                score += 5
 
        score = max(0, min(score, 100))
    else:
        score = 70  # no podcast/audio content on this page -- not applicable
 
    details = {
        "audio_elements": len(audio_elements),
        "podcast_platform_embeds": len(podcast_embeds),
        "show_notes_section_found": show_notes_heading is not None,
        "show_notes_word_count": show_notes_word_count,
        "show_notes_has_timestamps": show_notes_has_timestamps,
        "transcript_section_found": transcript_heading is not None,
        "transcript_word_count": transcript_word_count,
        "substantial_transcript_present": has_substantial_transcript,
        "podcast_schema_present": has_podcast_schema,
        "schema_includes_transcript": schema_has_transcript
    }
 
    recommendations = []
 
    if has_podcast_content and score < 75:
 
        if not has_substantial_transcript:
            recommendations.append(
                "Publish a full, substantial written transcript of the episode — transcripts are required for "
                "podcast content to be cited in AI-generated answers, since audio itself typically isn't ingested."
            )
 
        if not has_substantial_show_notes:
            recommendations.append(
                "Add detailed show notes summarizing what the episode covers, not just a one-line description."
            )
 
        if has_substantial_show_notes and not show_notes_has_timestamps:
            recommendations.append(
                "Include timestamps in the show notes so specific segments/topics can be referenced precisely."
            )
 
        if not has_podcast_schema:
            recommendations.append(
                "Add PodcastEpisode/PodcastSeries structured data (schema.org) to make the episode and its "
                "metadata machine-readable."
            )
 
        if has_podcast_schema and not schema_has_transcript:
            recommendations.append(
                "Include the transcript in the PodcastEpisode schema's transcript field, not just as body text."
            )
 
    return {
        "factor": "Podcast Show Notes with Transcripts",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_podcast_show_notes_transcripts