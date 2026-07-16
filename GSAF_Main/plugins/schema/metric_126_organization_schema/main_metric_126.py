from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="126 - Organization Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "organization_found": False,
        "organization_name": None,
        "logo": None,
        "sameAs_links": []
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                schema_type = item.get("@type")
                is_organization = False
                if isinstance(schema_type, list):
                    is_organization = "Organization" in schema_type
                else:
                    is_organization = schema_type == "Organization"
                    
                if is_organization:
                    result.details["organization_found"] = True
                    result.details["organization_name"] = item.get("name")
                    result.details["logo"] = item.get("logo")
                    result.details["sameAs_links"] = item.get("sameAs", [])
                    
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Add Organization schema to help search engines understand your brand.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
