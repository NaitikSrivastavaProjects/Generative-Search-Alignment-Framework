def build_site_data(url, keyword="", keywords=None, competitor_url=""):
    return {
        "url": url,
        "keyword": keyword,
        "keywords": keywords or [],
        "competitor_url": competitor_url
    }