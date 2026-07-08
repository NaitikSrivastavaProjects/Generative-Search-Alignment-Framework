from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="31 - WebSite Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "website_schema_found": False,
        "website_name": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "WebSite":
                    result.details["website_schema_found"] = True
                    result.details["website_name"] = item.get("name")
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Add WebSite schema to the homepage to help search engines understand the site structure and provide a Sitelinks Search Box.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
