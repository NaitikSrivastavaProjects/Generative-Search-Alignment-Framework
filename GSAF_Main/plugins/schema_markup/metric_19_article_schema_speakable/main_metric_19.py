'''
Article Schema with Speakable Property Checker:
Detects whether Article schema includes the 'speakable' property.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_article_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if any(t in ("Article", "NewsArticle", "BlogPosting") for t in types):
            found.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_article_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_article_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="19 - Article Schema with Speakable Property")
    try:
        blocks = site_data.json_ld
        article_blocks = []
        for b in blocks:
            article_blocks.extend(_find_article_blocks(b))

        if not article_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No Article/NewsArticle/BlogPosting schema found"
            result.recommendations.append("Add Article schema if this is an article page.")
            return result.to_dict()

        has_speakable = any("speakable" in b for b in article_blocks)
        score = 100 if has_speakable else 40

        result.score = score
        result.status = get_status(score)
        result.details["article_schema_found"] = True
        result.details["has_speakable"] = has_speakable

        if not has_speakable:
            result.recommendations.append("Add the 'speakable' property to your Article schema to mark sections for voice assistants.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()