from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="132 - WebPage Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "webpage_schema_found": False,
        "page_name": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "WebPage":
                    result.details["webpage_schema_found"] = True
                    result.details["page_name"] = item.get("name")
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding WebPage schema to provide more context about the specific page's purpose and contents.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
