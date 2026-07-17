'''
Person Schema for Authors Checker:
Detects whether author pages/bylines include Person schema with
credentials and expertise.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_person_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if "Person" in types:
            found.append(data)
        author = data.get("author")
        if isinstance(author, dict):
            author_type = author.get("@type", "")
            author_types = author_type if isinstance(author_type, list) else [author_type]
            if "Person" in author_types:
                found.append(author)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_person_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_person_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="28 - Person Schema for Authors")
    try:
        blocks = site_data.json_ld
        person_blocks = []
        for b in blocks:
            person_blocks.extend(_find_person_blocks(b))

        if not person_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No Person schema found for author"
            result.recommendations.append("Add Person schema for the article author with name and credentials.")
            return result.to_dict()

        block = person_blocks[0]
        has_name = bool(block.get("name"))
        has_credentials = bool(block.get("jobTitle")) or bool(block.get("description")) or bool(block.get("sameAs"))

        if has_name and has_credentials:
            score = 100
        elif has_name:
            score = 50
            result.recommendations.append("Add credentials/expertise info (jobTitle, description, or sameAs links) to Person schema.")
        else:
            score = 20
            result.recommendations.append("Add 'name' and credentials to Person schema.")

        result.score = score
        result.status = get_status(score)
        result.details["has_name"] = has_name
        result.details["has_credentials"] = has_credentials

    except Exception as e:
        result.error = str(e)

    return result.to_dict()