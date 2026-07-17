'''
Organization + sameAs Checker:
Detects whether Organization schema includes 'sameAs' links to
Wikipedia, Wikidata, and social profiles.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def _find_org_blocks(data, found=None):
    if found is None:
        found = []
    if isinstance(data, dict):
        type_val = data.get("@type", "")
        types = type_val if isinstance(type_val, list) else [type_val]
        if "Organization" in types:
            found.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                _find_org_blocks(item, found)
    elif isinstance(data, list):
        for item in data:
            _find_org_blocks(item, found)
    return found

def run(site_data):
    result = MetricResult(factor="27 - Organization + sameAs")
    try:
        blocks = site_data.json_ld
        org_blocks = []
        for b in blocks:
            org_blocks.extend(_find_org_blocks(b))

        if not org_blocks:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No Organization schema found"
            result.recommendations.append("Add Organization schema with 'sameAs' links to establish entity identity.")
            return result.to_dict()

        block = org_blocks[0]
        same_as = block.get("sameAs", [])
        if isinstance(same_as, str):
            same_as = [same_as]

        has_wikipedia = any("wikipedia.org" in link for link in same_as)
        has_wikidata = any("wikidata.org" in link for link in same_as)
        has_social = any(any(s in link for s in ["twitter.com", "x.com", "linkedin.com", "facebook.com", "instagram.com"]) for link in same_as)

        fields_present = sum([has_wikipedia, has_wikidata, has_social])
        score = round((fields_present / 3) * 100)

        result.score = score
        result.status = get_status(score)
        result.details["same_as_links"] = same_as

        if not has_wikipedia:
            result.recommendations.append("Add a Wikipedia link to 'sameAs'.")
        if not has_wikidata:
            result.recommendations.append("Add a Wikidata link to 'sameAs'.")
        if not has_social:
            result.recommendations.append("Add social profile links to 'sameAs'.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()