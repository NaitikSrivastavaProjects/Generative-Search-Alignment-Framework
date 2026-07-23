import json
 
 
VIDEO_OBJECT_REQUIRED_FIELDS = ["name", "description", "thumbnailUrl", "uploadDate"]
VIDEO_OBJECT_RECOMMENDED_FIELDS = ["contentUrl", "embedUrl", "duration", "transcript"]
 
PODCAST_SERIES_REQUIRED_FIELDS = ["name", "url"]
PODCAST_SERIES_RECOMMENDED_FIELDS = ["description", "webFeed"]
 
PODCAST_EPISODE_REQUIRED_FIELDS = ["name", "datePublished"]
PODCAST_EPISODE_RECOMMENDED_FIELDS = ["description", "associatedMedia", "partOfSeries", "transcript"]
 
RELEVANT_TYPES = ["VideoObject", "PodcastSeries", "PodcastEpisode"]
 
 
def _extract_json_ld_blocks(soup):
    blocks = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
 
        candidates = data if isinstance(data, list) else [data]
        for block in candidates:
            if isinstance(block, dict):
                blocks.append(block)
                # some publishers nest relevant types inside @graph
                graph = block.get("@graph")
                if isinstance(graph, list):
                    blocks.extend(b for b in graph if isinstance(b, dict))
    return blocks
 
 
def _score_schema_block(block, required_fields, recommended_fields):
    present_required = [f for f in required_fields if block.get(f)]
    present_recommended = [f for f in recommended_fields if block.get(f)]
    missing_required = [f for f in required_fields if f not in present_required]
    missing_recommended = [f for f in recommended_fields if f not in present_recommended]
 
    completeness = (
        (len(present_required) / len(required_fields)) * 0.7
        + (len(present_recommended) / len(recommended_fields)) * 0.3
    ) if required_fields or recommended_fields else 0
 
    return {
        "present_required": present_required,
        "missing_required": missing_required,
        "present_recommended": present_recommended,
        "missing_recommended": missing_recommended,
        "completeness_pct": round(completeness * 100, 1)
    }
 
 
def analyze_video_podcast_schema(site_data):
 
    soup = site_data.soup
 
    has_video_element = bool(soup.find_all("video"))
    has_podcast_audio = bool(soup.find_all("audio"))
    has_video_iframe_embed = any(
        any(d in (iframe.get("src") or "").lower() for d in ["youtube.com", "youtube-nocookie.com", "vimeo.com", "wistia"])
        for iframe in soup.find_all("iframe", src=True)
    )
    has_podcast_iframe_embed = any(
        any(d in (iframe.get("src") or "").lower() for d in ["open.spotify.com", "buzzsprout.com", "libsyn.com", "anchor.fm", "podbean.com"])
        for iframe in soup.find_all("iframe", src=True)
    )
 
    blocks = _extract_json_ld_blocks(soup)
 
    video_blocks = [b for b in blocks if b.get("@type") == "VideoObject"]
    podcast_series_blocks = [b for b in blocks if b.get("@type") == "PodcastSeries"]
    podcast_episode_blocks = [b for b in blocks if b.get("@type") == "PodcastEpisode"]
 
    has_video_media = has_video_element or has_video_iframe_embed
    has_podcast_media = has_podcast_audio or has_podcast_iframe_embed
 
    video_analysis = None
    if video_blocks:
        video_analysis = _score_schema_block(
            video_blocks[0], VIDEO_OBJECT_REQUIRED_FIELDS, VIDEO_OBJECT_RECOMMENDED_FIELDS
        )
 
    podcast_series_analysis = None
    if podcast_series_blocks:
        podcast_series_analysis = _score_schema_block(
            podcast_series_blocks[0], PODCAST_SERIES_REQUIRED_FIELDS, PODCAST_SERIES_RECOMMENDED_FIELDS
        )
 
    podcast_episode_analysis = None
    if podcast_episode_blocks:
        podcast_episode_analysis = _score_schema_block(
            podcast_episode_blocks[0], PODCAST_EPISODE_REQUIRED_FIELDS, PODCAST_EPISODE_RECOMMENDED_FIELDS
        )
 
    applicable = has_video_media or has_podcast_media
 
    if not applicable:
        score = 70  # no video/podcast content on this page -- not applicable, not penalized
    else:
        component_scores = []
 
        if has_video_media:
            component_scores.append(video_analysis["completeness_pct"] if video_analysis else 0)
 
        if has_podcast_media:
            # average whichever podcast schema types are relevant/present
            podcast_component_scores = []
            if podcast_series_analysis:
                podcast_component_scores.append(podcast_series_analysis["completeness_pct"])
            if podcast_episode_analysis:
                podcast_component_scores.append(podcast_episode_analysis["completeness_pct"])
            if not podcast_component_scores:
                podcast_component_scores.append(0)
            component_scores.append(sum(podcast_component_scores) / len(podcast_component_scores))
 
        score = round(sum(component_scores) / len(component_scores)) if component_scores else 0
 
    score = max(0, min(score, 100))
 
    details = {
        "has_video_media_on_page": has_video_media,
        "has_podcast_media_on_page": has_podcast_media,
        "video_object_schema_found": bool(video_blocks),
        "video_object_analysis": video_analysis,
        "podcast_series_schema_found": bool(podcast_series_blocks),
        "podcast_series_analysis": podcast_series_analysis,
        "podcast_episode_schema_found": bool(podcast_episode_blocks),
        "podcast_episode_analysis": podcast_episode_analysis
    }
 
    recommendations = []
 
    if applicable and score < 75:
 
        if has_video_media and not video_blocks:
            recommendations.append(
                "Add VideoObject structured data (schema.org) for video content on this page — it's required "
                "for video content to be properly indexed and cited by AI engines."
            )
        elif has_video_media and video_analysis and video_analysis["missing_required"]:
            recommendations.append(
                "VideoObject schema is missing required fields: " + ", ".join(video_analysis["missing_required"]) + "."
            )
        elif has_video_media and video_analysis and video_analysis["missing_recommended"]:
            recommendations.append(
                "Strengthen VideoObject schema by adding: " + ", ".join(video_analysis["missing_recommended"]) + "."
            )
 
        if has_podcast_media and not podcast_series_blocks and not podcast_episode_blocks:
            recommendations.append(
                "Add PodcastSeries and/or PodcastEpisode structured data (schema.org) for podcast content on this page."
            )
        else:
            if podcast_series_analysis and podcast_series_analysis["missing_required"]:
                recommendations.append(
                    "PodcastSeries schema is missing required fields: " + ", ".join(podcast_series_analysis["missing_required"]) + "."
                )
            if podcast_episode_analysis and podcast_episode_analysis["missing_required"]:
                recommendations.append(
                    "PodcastEpisode schema is missing required fields: " + ", ".join(podcast_episode_analysis["missing_required"]) + "."
                )
 
    return {
        "factor": "Schema for Videos and Podcasts",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_video_podcast_schema