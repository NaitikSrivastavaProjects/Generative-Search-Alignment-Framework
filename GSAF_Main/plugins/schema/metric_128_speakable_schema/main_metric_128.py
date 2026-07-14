from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="28 - Speakable Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "speakable_found": False,
        "css_selectors": []
    }
    
    try:
        for data in site_data.json_ld:
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "SpeakableSpecification":
                    result.details["speakable_found"] = True
                    selectors = item.get("cssSelector", [])
                    if isinstance(selectors, str):
                        selectors = [selectors]
                    result.details["css_selectors"] = selectors
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Consider adding Speakable schema for sections of the page that are suitable for TTS playback.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
