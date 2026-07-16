from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="135 - Date Published & Modified")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "date_published": None,
        "date_modified": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    pub_date = item.get("datePublished")
                    mod_date = item.get("dateModified")
                    
                    if pub_date:
                        result.details["date_published"] = pub_date
                    if mod_date:
                        result.details["date_modified"] = mod_date
                        
                    if pub_date or mod_date:
                        result.status = "Success"
                        result.score = 100
                        return result.to_dict()
                    
        result.recommendations.append("Include 'datePublished' and 'dateModified' in your schema to help search engines understand content freshness.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
