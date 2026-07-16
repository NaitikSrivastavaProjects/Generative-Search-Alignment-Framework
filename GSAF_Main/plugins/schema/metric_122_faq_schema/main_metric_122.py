from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="122 - FAQPage Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "faq_found": False,
        "total_questions": 0,
        "questions": []
    }
    
    try:
        for data in site_data.json_ld:
            items = []
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict):
                if "@graph" in data:
                    items = data["@graph"]
                else:
                    items = [data]
                    
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "FAQPage":
                    result.details["faq_found"] = True
                    questions = item.get("mainEntity", [])
                    for question in questions:
                        if isinstance(question, dict):
                            result.details["questions"].append(question.get("name"))
                    result.details["total_questions"] = len(result.details["questions"])
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Add FAQPage schema markup to help appear in 'People Also Ask' results.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
