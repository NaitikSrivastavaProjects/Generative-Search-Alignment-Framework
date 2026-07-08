from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="34 - Publisher Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "publisher_found": False,
        "publisher_name": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    publisher = item.get("publisher")
                    if publisher:
                        result.details["publisher_found"] = True
                        if isinstance(publisher, dict):
                            result.details["publisher_name"] = publisher.get("name")
                        result.status = "Success"
                        result.score = 100
                        return result.to_dict()
                    
        result.recommendations.append("Include the 'publisher' property in your Article or NewsArticle schema to establish authoritativeness.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
