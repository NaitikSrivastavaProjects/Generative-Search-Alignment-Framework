"""
Factor 219

YouTube Integration
"""

from models.metric_result import MetricResult


def run(site_data):
    result = MetricResult(factor="219 - YouTube Integration")

    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        youtube_embeds = soup.find_all("iframe", src=True)
        youtube_found = any("youtube.com" in iframe["src"].lower() for iframe in youtube_embeds)
        score = 100 if youtube_found else 0
        result.score = score
        result.status = "Found" if score == 100 else "Not Found"
        result.details["youtube_embed_found"] = youtube_found
        result.details["iframe_count"] = len(youtube_embeds)
        result.details["raw_html_available"] = bool(raw_html)

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()
