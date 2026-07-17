'''
List Snippet Item Count Checker:
Detects whether lists have 6-8 items — fewer looks incomplete, more
triggers a "show more" link that reduces snippet visibility.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="32 - List Snippet Item Count")
    try:
        lists = site_data.soup.find_all(["ul", "ol"])
        if not lists:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No lists found on page"
            return result.to_dict()

        checked = []
        good_count = 0
        for lst in lists:
            item_count = len(lst.find_all("li", recursive=False))
            if item_count == 0:
                continue
            in_range = 6 <= item_count <= 8
            if in_range:
                good_count += 1
            checked.append({"item_count": item_count, "in_range": in_range})

        if not checked:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No non-empty lists found"
            return result.to_dict()

        score = round((good_count / len(checked)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["total_lists"] = len(checked)
        result.details["lists_in_range"] = good_count

        if score < 50:
            result.recommendations.append("Aim for 6-8 items per list for optimal snippet extraction — avoid too few or too many.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()