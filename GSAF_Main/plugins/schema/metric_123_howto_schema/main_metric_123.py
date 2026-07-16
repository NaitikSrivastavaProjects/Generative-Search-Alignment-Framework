from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="123 - HowTo Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "howto_found": False,
        "total_steps": 0
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "HowTo":
                    result.details["howto_found"] = True
                    steps = item.get("step", [])
                    result.details["total_steps"] = len(steps)
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding HowTo schema if your content provides step-by-instructions.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
