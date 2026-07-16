from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="124 - Dataset Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "dataset_found": False,
        "dataset_name": None,
        "description": None,
        "creator": None,
        "license": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                schema_type = item.get("@type")
                is_dataset = False
                if isinstance(schema_type, list):
                    is_dataset = "Dataset" in schema_type
                else:
                    is_dataset = schema_type == "Dataset"
                    
                if is_dataset:
                    result.details["dataset_found"] = True
                    result.details["dataset_name"] = item.get("name")
                    result.details["description"] = item.get("description")
                    
                    creator = item.get("creator")
                    if isinstance(creator, dict):
                        result.details["creator"] = creator.get("name")
                    else:
                        result.details["creator"] = creator
                        
                    result.details["license"] = item.get("license")
                    
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding Dataset schema if your page provides tabular data or datasets.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
