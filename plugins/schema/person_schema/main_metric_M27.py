from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="27 - Person Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "person_schema_found": False,
        "person_name": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Person":
                    result.details["person_schema_found"] = True
                    result.details["person_name"] = item.get("name")
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding Person schema if the page is about a specific individual or author.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
