from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="21 - Article + Author Schema")
    result.score = 0
    result.status = "Failed"
    result.details = {
        "article_schema_found": False,
        "author_found": False,
        "author_name": None,
        "headline": None,
        "date_published": None,
        "article_type": None
    }
    
    try:
        article_types = ["Article", "NewsArticle", "BlogPosting", "TechArticle", "LiveBlogPosting"]
        
        for data in site_data.json_ld:
            items = []
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    items.extend(data["@graph"])
                else:
                    items.append(data)
                    
            for item in items:
                if not isinstance(item, dict):
                    continue
                schema_type = item.get("@type")
                is_article = False
                if isinstance(schema_type, list):
                    is_article = any(t in article_types for t in schema_type)
                else:
                    is_article = schema_type in article_types
                    
                if is_article:
                    result.details["article_schema_found"] = True
                    result.details["article_type"] = schema_type
                    result.details["headline"] = item.get("headline")
                    result.details["date_published"] = item.get("datePublished")
                    
                    author = item.get("author")
                    if author:
                        result.details["author_found"] = True
                        if isinstance(author, dict):
                            result.details["author_name"] = author.get("name")
                        elif isinstance(author, list):
                            names = [p.get("name") for p in author if isinstance(p, dict) and p.get("name")]
                            names.extend([p for p in author if isinstance(p, str)])
                            result.details["author_name"] = ", ".join(names)
                        elif isinstance(author, str):
                            result.details["author_name"] = author
                    
                    result.status = "Success"
                    result.score = 100
                    return result.to_dict()
                    
        result.recommendations.append("Add Article and Author schema markup to improve rich results.")
    except Exception as e:
        result.error = str(e)

    return result.to_dict()
