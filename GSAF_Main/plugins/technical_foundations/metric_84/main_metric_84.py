from models.metric_result import MetricResult
from utils.helpers import get_status


def check_heading_hierarchy(soup):
    headings = [int(h.name[1]) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    if not headings:
        return False
    for i in range(1, len(headings)):
        if headings[i] - headings[i - 1] > 1:
            return False
    return True


def run(site_data):
    result = MetricResult(factor="84 - Clean Semantic HTML")

    try:
        soup = site_data.soup

        h1_tags = soup.find_all("h1")
        semantic_tags = soup.find_all(["article", "main", "section", "nav", "header", "footer"])
        lists = soup.find_all(["ul", "ol"])
        tables = soup.find_all("table")
        hierarchy_clean = check_heading_hierarchy(soup)

        result.details["h1_count"] = len(h1_tags)
        result.details["semantic_tags_found"] = list(set(tag.name for tag in semantic_tags))
        result.details["proper_lists"] = len(lists)
        result.details["proper_tables"] = len(tables)
        result.details["heading_hierarchy_clean"] = hierarchy_clean

        result.score = 0

        if len(h1_tags) == 1:
            result.score += 30
        else:
            result.recommendations.append(
                f"Found {len(h1_tags)} H1 tags — there should be exactly one per page."
            )

        if semantic_tags:
            result.score += 20
        else:
            result.recommendations.append(
                "No semantic tags found (article, main, section) — use these to structure content properly."
            )

        if hierarchy_clean:
            result.score += 20
        else:
            result.recommendations.append(
                "Heading hierarchy skips levels (e.g. H1 to H3 without H2) — fix the heading order."
            )

        if lists:
            result.score += 15
        else:
            result.recommendations.append(
                "No proper list tags (ul/ol) found — avoid using line breaks to simulate lists."
            )

        if tables:
            result.score += 15

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()