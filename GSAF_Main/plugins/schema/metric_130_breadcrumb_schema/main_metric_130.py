from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="130 - Breadcrumb Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "breadcrumb_found": False,
        "total_items": 0
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "BreadcrumbList":
                    result.details["breadcrumb_found"] = True
                    items_list = item.get("itemListElement", [])
                    result.details["total_items"] = len(items_list)
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Add BreadcrumbList schema to improve site navigation in search results.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
