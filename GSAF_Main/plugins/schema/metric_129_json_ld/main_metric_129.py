from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="129 - JSON-LD Schema Validation")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "jsonld_found": False,
        "total_blocks": 0,
        "schema_types": []
    }
    
    try:
        if site_data.json_ld:
            result.details["jsonld_found"] = True
            result.details["total_blocks"] = len(site_data.json_ld)
            
            schema_types = []
            for data in site_data.json_ld:
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    schema_type = item.get("@type")
                    if not schema_type:
                        continue
                    if isinstance(schema_type, list):
                        schema_types.extend(schema_type)
                    else:
                        schema_types.append(schema_type)
                        
            result.details["schema_types"] = list(set(schema_types))
            result.status = "Success"
            result.score = 100 if schema_types else 50
        else:
            result.recommendations.append("Consider using JSON-LD for structured data, as it is the format recommended by Google.")
    except Exception as e:
        result.error = str(e)
        
    return result.to_dict()
