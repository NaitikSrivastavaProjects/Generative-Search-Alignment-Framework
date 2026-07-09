from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="33 - Logo Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "logo_found": False,
        "logo_url": None
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Organization":
                    logo = item.get("logo")
                    if logo:
                        result.details["logo_found"] = True
                        if isinstance(logo, dict):
                            result.details["logo_url"] = logo.get("url")
                        else:
                            result.details["logo_url"] = logo
                        result.status = "Success"
                        result.score = 100
                        return result.to_dict()
                    
        result.recommendations.append("Ensure your Organization schema includes a 'logo' property so search engines can display it in the Knowledge Panel.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
