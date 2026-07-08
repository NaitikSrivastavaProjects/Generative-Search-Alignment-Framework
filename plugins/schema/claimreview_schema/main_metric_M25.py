from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="25 - ClaimReview Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "claimreview_found": False,
        "reviewed_claim": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "ClaimReview":
                    result.details["claimreview_found"] = True
                    result.details["reviewed_claim"] = item.get("claimReviewed")
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding ClaimReview schema if your content fact-checks claims.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
